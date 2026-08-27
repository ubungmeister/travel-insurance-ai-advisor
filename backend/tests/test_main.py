from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_returns_reply():
    response = client.post("/api/v1/chat", json={"message": "Am I covered?"})
    assert response.status_code == 200
    body = response.json()
    assert "reply" in body
    assert "Am I covered?" in body["reply"]


def test_chat_rejects_blank_message():
    response = client.post("/api/v1/chat", json={"message": "   "})
    assert response.status_code == 422


def test_chat_rejects_missing_message():
    response = client.post("/api/v1/chat", json={})
    assert response.status_code == 422


def test_chat_rejects_oversized_message():
    response = client.post("/api/v1/chat", json={"message": "a" * 2001})
    assert response.status_code == 422


def test_chat_rejects_unknown_fields():
    response = client.post(
        "/api/v1/chat", json={"message": "hello", "role": "admin"}
    )
    assert response.status_code == 422
