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
