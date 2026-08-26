from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_create_trace():
    payload = {
        "application": "support-agent",
        "environment": "production",
        "model": "test-model",
        "user_input": "Can I cancel my subscription?",
        "prompt": "Answer the user using the provided policy.",
        "model_output": "Yes, you can cancel your subscription.",
    }

    response = client.post("/v1/traces", json=payload)

    assert response.status_code == 201

    body = response.json()

    assert body["status"] == "accepted"
    assert "trace_id" in body
    assert body["trace_id"]

def test_create_trace_rejects_invalid_environment():
    payload = {
        "application": "support-agent",
        "environment": "mars",
        "model": "test-model",
        "user_input": "Hello",
        "prompt": "Respond to the user.",
    }

    response = client.post("/v1/traces", json=payload)

    assert response.status_code == 422

def test_create_trace_rejects_empty_application():
    payload = {
        "application": "",
        "environment": "production",
        "model": "test-model",
        "user_input": "Hello",
        "prompt": "Respond to the user.",
    }

    response = client.post("/v1/traces", json=payload)

    assert response.status_code == 422


def test_create_trace_rejects_missing_model():
    payload = {
        "application": "support-agent",
        "environment": "production",
        "user_input": "Hello",
        "prompt": "Respond to the user.",
    }

    response = client.post("/v1/traces", json=payload)

    assert response.status_code == 422


def test_create_trace_allows_missing_model_output():
    payload = {
        "application": "support-agent",
        "environment": "production",
        "model": "test-model",
        "user_input": "Hello",
        "prompt": "Respond to the user.",
    }

    response = client.post("/v1/traces", json=payload)

    assert response.status_code == 201