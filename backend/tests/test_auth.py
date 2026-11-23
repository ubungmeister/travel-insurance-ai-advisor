import time
from datetime import datetime, timezone
from uuid import uuid4

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi.testclient import TestClient

from app.dependencies import authentication
from app.main import app

client = TestClient(app)

LOGIN_URL = "/api/auth/login"
REFRESH_URL = "/api/auth/refresh"
LOGOUT_URL = "/api/auth/logout"
ME_URL = "/api/auth/me"


def _mock_post(monkeypatch, response: httpx.Response | None = None, error: Exception | None = None):
    def fake_post(*args, **kwargs):
        if error is not None:
            raise error
        return response

    monkeypatch.setattr(httpx, "post", fake_post)


def test_login_success(monkeypatch):
    _mock_post(
        monkeypatch,
        response=httpx.Response(
            200,
            json={
                "access_token": "access-token",
                "refresh_token": "refresh-token",
                "token_type": "bearer",
                "expires_in": 3600,
                "expires_at": 1234567890,
            },
        ),
    )

    response = client.post(
        LOGIN_URL, json={"email": "demo@example.com", "password": "password123"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] == "access-token"
    assert body["expires_in"] == 3600
    assert body["expires_at"] == 1234567890


def test_login_rejects_bad_credentials(monkeypatch):
    _mock_post(
        monkeypatch,
        response=httpx.Response(400, json={"error": "invalid_grant"}),
    )

    response = client.post(
        LOGIN_URL, json={"email": "demo@example.com", "password": "wrong"}
    )

    assert response.status_code == 401


def test_login_rejects_rate_limit(monkeypatch):
    _mock_post(
        monkeypatch,
        response=httpx.Response(429, json={"error": "over_request_rate_limit"}),
    )

    response = client.post(
        LOGIN_URL, json={"email": "demo@example.com", "password": "password123"}
    )

    assert response.status_code == 429


def test_login_returns_503_when_supabase_unreachable(monkeypatch):
    _mock_post(monkeypatch, error=httpx.ConnectError("boom"))

    response = client.post(
        LOGIN_URL, json={"email": "demo@example.com", "password": "password123"}
    )

    assert response.status_code == 503


def test_login_returns_502_on_malformed_response(monkeypatch):
    _mock_post(
        monkeypatch,
        response=httpx.Response(200, json={"access_token": "only-this"}),
    )

    response = client.post(
        LOGIN_URL, json={"email": "demo@example.com", "password": "password123"}
    )

    assert response.status_code == 502


def test_refresh_success(monkeypatch):
    _mock_post(
        monkeypatch,
        response=httpx.Response(
            200,
            json={
                "access_token": "new-access-token",
                "refresh_token": "new-refresh-token",
                "token_type": "bearer",
                "expires_in": 3600,
                "expires_at": 1234567890,
            },
        ),
    )

    response = client.post(REFRESH_URL, json={"refresh_token": "old-refresh-token"})

    assert response.status_code == 200
    assert response.json()["access_token"] == "new-access-token"


def test_refresh_rejects_invalid_token(monkeypatch):
    _mock_post(
        monkeypatch,
        response=httpx.Response(400, json={"error": "invalid_grant"}),
    )

    response = client.post(REFRESH_URL, json={"refresh_token": "bad-refresh-token"})

    assert response.status_code == 401


def test_refresh_does_not_require_access_token(monkeypatch):
    _mock_post(
        monkeypatch,
        response=httpx.Response(
            200,
            json={
                "access_token": "new-access-token",
                "refresh_token": "new-refresh-token",
                "token_type": "bearer",
                "expires_in": 3600,
                "expires_at": 1234567890,
            },
        ),
    )

    # no Authorization header at all — refresh must work with an expired/absent access token
    response = client.post(REFRESH_URL, json={"refresh_token": "old-refresh-token"})

    assert response.status_code == 200


def test_logout_success(monkeypatch):
    _mock_post(monkeypatch, response=httpx.Response(204))

    response = client.post(
        LOGOUT_URL, headers={"Authorization": "Bearer some-access-token"}
    )

    assert response.status_code == 204


def test_logout_requires_token():
    response = client.post(LOGOUT_URL)
    assert response.status_code == 401


def test_logout_rejects_invalid_token(monkeypatch):
    _mock_post(monkeypatch, response=httpx.Response(401, json={"error": "invalid_token"}))

    response = client.post(
        LOGOUT_URL, headers={"Authorization": "Bearer bad-token"}
    )

    assert response.status_code == 401


def test_logout_returns_503_when_supabase_unreachable(monkeypatch):
    _mock_post(monkeypatch, error=httpx.ConnectError("boom"))

    response = client.post(
        LOGOUT_URL, headers={"Authorization": "Bearer some-access-token"}
    )

    assert response.status_code == 503


@pytest.fixture
def keypair():
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_key, public_pem


def _make_token(private_key, *, email="demo@example.com", expires_in=3600, sub=None):
    now = int(time.time())
    payload = {
        "sub": sub or str(uuid4()),
        "email": email,
        "aud": authentication.settings.supabase_jwt_audience,
        "iss": authentication.SUPABASE_ISSUER,
        "iat": now,
        "exp": now + expires_in,
    }
    return jwt.encode(payload, private_key, algorithm="ES256")


def test_me_returns_current_user(monkeypatch, keypair):
    private_key, public_pem = keypair
    monkeypatch.setattr(
        authentication.jwks_client,
        "get_signing_key_from_jwt",
        lambda token: type("SigningKey", (), {"key": public_pem})(),
    )
    token = _make_token(private_key, email="demo@example.com")

    response = client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == "demo@example.com"


def test_me_requires_auth():
    response = client.get(ME_URL)
    assert response.status_code == 401


@pytest.mark.parametrize(
    ("claims", "expected"),
    [
        ({"iat": 1}, 200),
        ({"iat": 2}, 200),
        ({"iat": 3}, 401),
        ({"iat": "invalid"}, 401),
        ({"exp": -1}, 401),
        ({"nbf": 1}, 401),
    ],
    ids=[
        "initial-request", "iat-boundary", "too-early", "invalid-iat", "expired", "not-before",
    ],
)
def test_me_applies_clock_tolerance_only_to_issued_at(
    monkeypatch, keypair, claims, expected
):
    private_key, public_pem = keypair
    now = datetime(2026, 11, 20, tzinfo=timezone.utc)
    timestamp = int(now.timestamp())

    class FixedClock(datetime):
        @classmethod
        def now(cls, tz=None):
            return now.astimezone(tz) if tz else now.replace(tzinfo=None)

    monkeypatch.setattr(jwt.api_jwt, "datetime", FixedClock)
    monkeypatch.setattr(authentication, "datetime", FixedClock, raising=False)
    monkeypatch.setattr(
        authentication.jwks_client,
        "get_signing_key_from_jwt",
        lambda token: type("SigningKey", (), {"key": public_pem})(),
    )
    payload = {
        "sub": str(uuid4()),
        "email": "demo@example.com",
        "aud": authentication.settings.supabase_jwt_audience,
        "iss": authentication.SUPABASE_ISSUER,
        "iat": timestamp - 10,
        "exp": timestamp + 60,
        **{
            claim: timestamp + offset if isinstance(offset, int) else offset
            for claim, offset in claims.items()
        },
    }
    token = jwt.encode(payload, private_key, algorithm="ES256")
    response = client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == expected
    if expected == 401:
        assert response.json() == {"detail": "Invalid or expired token"}


def test_me_rejects_invalid_signature(monkeypatch, keypair):
    _private_key, public_pem = keypair
    other_private_key = ec.generate_private_key(ec.SECP256R1())
    monkeypatch.setattr(
        authentication.jwks_client,
        "get_signing_key_from_jwt",
        lambda token: type("SigningKey", (), {"key": public_pem})(),
    )
    token = _make_token(other_private_key)

    response = client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_me_rejects_expired_token(monkeypatch, keypair):
    private_key, public_pem = keypair
    monkeypatch.setattr(
        authentication.jwks_client,
        "get_signing_key_from_jwt",
        lambda token: type("SigningKey", (), {"key": public_pem})(),
    )
    token = _make_token(private_key, expires_in=-3600)

    response = client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
