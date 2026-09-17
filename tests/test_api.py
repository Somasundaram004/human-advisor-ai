from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_memory_advice_and_learning_are_available():
    response = client.post("/v1/memories", json={"kind": "incident", "summary": "Test incident"})
    assert response.status_code == 200
    response = client.post("/v1/advice", json={"question": "What happened?"})
    assert response.status_code == 200
    assert response.json()["requires_human_decision"] is False
    assert response.json()["answer_source"] == "local"
    assert "AI_API_KEY" not in response.json()["answer"]
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


def test_voice_requires_consent_and_can_be_stopped():
    response = client.post("/v1/voice/start", json={"consent": False})
    assert response.json()["requires_explicit_consent"] is True
    response = client.post("/v1/voice/start", json={"consent": True})
    assert response.json()["active"] is True
    response = client.post("/v1/voice/stop")
    assert response.json()["active"] is False


def test_brosir_wake_word_activates_only_after_consent():
    client.post("/v1/voice/stop")
    response = client.post("/v1/voice/command", json={"text": "Brosir remember this", "speaker": "human"})
    assert response.json()["accepted"] is False
    client.post("/v1/voice/start", json={"consent": True})
    response = client.post("/v1/voice/command", json={"text": "Brosir remember this", "speaker": "human"})
    assert response.json()["activated"] is True
    assert response.json()["command"] == "remember this"
    response = client.post("/v1/voice/command", json={"text": "Now remember the next detail", "speaker": "human"})
    assert response.json()["accepted"] is True
    assert response.json()["wake_word_detected"] is False
    assert response.json()["continuous_session"] is True
    assert response.json()["answer"]


def test_critical_voice_request_requires_approval():
    client.post("/v1/voice/stop")
    client.post("/v1/voice/start", json={"consent": True})
    client.post("/v1/voice/command", json={"text": "Brosir hello", "speaker": "human"})
    response = client.post("/v1/voice/command", json={"text": "deploy this to production", "speaker": "human"})
    assert response.json()["critical_action"] is True
    assert response.json()["human_approval_required"] is True


def test_local_adviser_answers_without_api_key():
    response = client.post("/v1/advice", json={"question": "How should I investigate an outage?"})
    assert response.status_code == 200
    assert response.json()["answer_source"] == "local"
    assert "timeline" in response.json()["answer"]