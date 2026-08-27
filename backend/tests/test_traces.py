from uuid import UUID, uuid4

from sqlalchemy import select

from backend.app.models.trace import Trace


def test_create_trace(client, db_session):
    payload = {
        "application": "support-agent",
        "environment": "production",
        "model": "test-model",
        "user_input": "Can I cancel my subscription?",
        "prompt": "Answer the user using the provided policy.",
        "model_output": "Yes, you can cancel your subscription.",
    }

    # 1. Send the request to our API
    response = client.post("/v1/traces", json=payload)

    # 2. Verify the API response
    assert response.status_code == 201

    body = response.json()

    assert body["status"] == "accepted"
    assert body["trace_id"]

    # 3. Query PostgreSQL directly using the ID returned by the API
    stored_trace = db_session.scalar(
        select(Trace).where(
            Trace.id == UUID(body["trace_id"])
        )
    )

    # 4. Verify that the row really exists in PostgreSQL
    assert stored_trace is not None
    assert stored_trace.application == "support-agent"
    assert stored_trace.environment == "production"
    assert stored_trace.model == "test-model"

def test_create_trace_rejects_invalid_environment(client):
    payload = {
        "application": "support-agent",
        "environment": "mars",
        "model": "test-model",
        "user_input": "Hello",
        "prompt": "Respond to the user.",
    }

    response = client.post("/v1/traces", json=payload)

    assert response.status_code == 422

def test_create_trace_rejects_empty_application(client):
    payload = {
        "application": "",
        "environment": "production",
        "model": "test-model",
        "user_input": "Hello",
        "prompt": "Respond to the user.",
    }

    response = client.post("/v1/traces", json=payload)

    assert response.status_code == 422


def test_create_trace_rejects_missing_model(client):
    payload = {
        "application": "support-agent",
        "environment": "production",
        "user_input": "Hello",
        "prompt": "Respond to the user.",
    }

    response = client.post("/v1/traces", json=payload)

    assert response.status_code == 422


def test_create_trace_allows_missing_model_output(client):
    payload = {
        "application": "support-agent",
        "environment": "production",
        "model": "test-model",
        "user_input": "Hello",
        "prompt": "Respond to the user.",
    }

    response = client.post("/v1/traces", json=payload)

    assert response.status_code == 201

def test_get_trace(client):
    payload = {
        "application": "support-agent",
        "environment": "production",
        "model": "test-model",
        "user_input": "Can I cancel my subscription?",
        "prompt": "Answer according to company policy.",
        "model_output": "Yes, you can cancel.",
    }

    create_response = client.post(
        "/v1/traces",
        json=payload,
    )

    assert create_response.status_code == 201

    trace_id = create_response.json()["trace_id"]

    get_response = client.get(
        f"/v1/traces/{trace_id}"
    )

    assert get_response.status_code == 200

    body = get_response.json()

    assert body["trace_id"] == trace_id
    assert body["application"] == "support-agent"
    assert body["environment"] == "production"
    assert body["model"] == "test-model"
    assert body["user_input"] == "Can I cancel my subscription?"
    assert body["model_output"] == "Yes, you can cancel."
    assert body["created_at"]

def test_get_trace_returns_404_when_not_found(client):
    missing_trace_id = uuid4()

    response = client.get(
        f"/v1/traces/{missing_trace_id}"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Trace not found"
    }