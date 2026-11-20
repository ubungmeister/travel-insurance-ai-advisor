from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

bearer_scheme = HTTPBearer(auto_error=False)

SUPABASE_ISSUER = f"{settings.supabase_url.rstrip('/')}/auth/v1"
ISSUED_AT_TOLERANCE_SECONDS = 2

jwks_client = jwt.PyJWKClient(f"{SUPABASE_ISSUER}/.well-known/jwks.json")


@dataclass(frozen=True)
class CurrentUser:
    auth_user_id: UUID
    email: str


def get_bearer_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return credentials.credentials


def get_current_user(
    token: str = Depends(get_bearer_token),
) -> CurrentUser:
    """Resolve an identity only after verifying a Supabase-issued bearer JWT.

    Validate the signature, issuer, audience, expiry and not-before claim via
    PyJWT. Check the issued-at claim separately because PyJWT's global leeway
    would also relax expiry and not-before; only fresh issuance gets a small
    allowance for clock drift. Keep token-validation details out of the 401.
    """
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience=settings.supabase_jwt_audience,
            issuer=SUPABASE_ISSUER,
            options={"verify_iat": False},
        )

        if "iat" in payload:
            issued_at = payload["iat"]
            if type(issued_at) is not int:
                raise jwt.InvalidIssuedAtError("Issued At must be an integer")
            now = datetime.now(timezone.utc).timestamp()
            if issued_at > now + ISSUED_AT_TOLERANCE_SECONDS:
                raise jwt.ImmatureSignatureError("Token issued in the future")

        auth_user_id = UUID(payload["sub"])
        email = payload["email"]

    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from None

    return CurrentUser(
        auth_user_id=auth_user_id,
        email=email,
    )
