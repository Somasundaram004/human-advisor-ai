from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_memory_advice_and_learning_are_available():
    response = client.post("/v1/memories", json={"kind": "incident", "summary": "Test incident"})
    assert response.status_code == 200
    response = client.post("/v1/advice", json={"question": "What happened?"})
    assert response.status_code == 200
    assert response.json()["requires_human_decision"] is True
    response = client.post("/v1/learning/feedback", json={"kind": "feedback", "summary": "Ask before changes"})
    assert response.status_code == 200
    assert client.get("/v1/learning/profile").json()["human_review_required"] is True


def test_actions_are_pending_and_not_executed():
    response = client.post("/v1/api/request", json={"action": "send_api_request", "reason": "Need approval", "payload": {"url": "https://example.com"}})
    assert response.status_code == 200
    assert response.json()["sent"] is False
    response = client.post("/v1/code/draft", json={"action": "write_code", "reason": "Need review", "payload": {"filename": "x.py", "content": "print(1)"}})
    assert response.status_code == 200
    assert response.json()["written"] is False