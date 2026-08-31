from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import select

from backend.app.models.trace import Trace


def create_trace(
    client,
    *,
    application: str = "support-agent",
    environment: str = "production",
    model: str = "test-model",
):
    response = client.post(
        "/v1/traces",
        json={
            "application": application,
            "environment": environment,
            "model": model,
            "user_input": "Test input",
            "prompt": "Test prompt",
            "model_output": "Test output",
        },
    )

    assert response.status_code == 201
    return response.json()


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

def test_list_traces(client):
    create_trace(client, application="support-agent")
    create_trace(client, application="billing-agent")

    response = client.get("/v1/traces")

    assert response.status_code == 200

    body = response.json()

    assert len(body["items"]) == 2
    assert body["limit"] == 20
    assert body["offset"] == 0

def test_list_traces_filters_by_application(client):
    create_trace(client, application="support-agent")
    create_trace(client, application="billing-agent")

    response = client.get(
        "/v1/traces",
        params={"application": "support-agent"},
    )

    assert response.status_code == 200

    items = response.json()["items"]

    assert len(items) == 1
    assert items[0]["application"] == "support-agent"

def test_list_traces_filters_by_environment(client):
    create_trace(client, environment="production")
    create_trace(client, environment="staging")

    response = client.get(
        "/v1/traces",
        params={"environment": "staging"},
    )

    assert response.status_code == 200

    items = response.json()["items"]

    assert len(items) == 1
    assert items[0]["environment"] == "staging"

def test_list_traces_filters_by_model(client):
    create_trace(client, model="model-a")
    create_trace(client, model="model-b")

    response = client.get(
        "/v1/traces",
        params={"model": "model-b"},
    )

    assert response.status_code == 200

    items = response.json()["items"]

    assert len(items) == 1
    assert items[0]["model"] == "model-b"

def test_list_traces_supports_combined_filters(client):
    create_trace(
        client,
        application="support-agent",
        environment="production",
        model="model-a",
    )

    create_trace(
        client,
        application="support-agent",
        environment="staging",
        model="model-a",
    )

    create_trace(
        client,
        application="billing-agent",
        environment="production",
        model="model-a",
    )

    response = client.get(
        "/v1/traces",
        params={
            "application": "support-agent",
            "environment": "production",
            "model": "model-a",
        },
    )

    assert response.status_code == 200

    items = response.json()["items"]

    assert len(items) == 1
    assert items[0]["application"] == "support-agent"
    assert items[0]["environment"] == "production"
    assert items[0]["model"] == "model-a"

def test_list_traces_applies_limit_and_offset(client):
    create_trace(client, application="app-1")
    create_trace(client, application="app-2")
    create_trace(client, application="app-3")

    response = client.get(
        "/v1/traces",
        params={
            "limit": 1,
            "offset": 1,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body["items"]) == 1
    assert body["limit"] == 1
    assert body["offset"] == 1

def test_list_traces_rejects_limit_above_maximum(client):
    response = client.get(
        "/v1/traces",
        params={"limit": 101},
    )

    assert response.status_code == 422

def test_list_traces_rejects_negative_offset(client):
    response = client.get(
        "/v1/traces",
        params={"offset": -1},
    )

    assert response.status_code == 422

def test_list_traces_rejects_invalid_environment(client):
    response = client.get(
        "/v1/traces",
        params={"environment": "mars"},
    )

    assert response.status_code == 422

def test_list_traces_orders_newest_first(client, db_session):
    older_time = datetime.now(UTC) - timedelta(hours=1)
    newer_time = datetime.now(UTC)

    older_trace = Trace(
        application="older-app",
        environment="production",
        model="test-model",
        user_input="Older input",
        prompt="Older prompt",
        model_output="Older output",
        created_at=older_time,
    )

    newer_trace = Trace(
        application="newer-app",
        environment="production",
        model="test-model",
        user_input="Newer input",
        prompt="Newer prompt",
        model_output="Newer output",
        created_at=newer_time,
    )

    db_session.add_all([older_trace, newer_trace])
    db_session.commit()

    response = client.get("/v1/traces")

    assert response.status_code == 200

    items = response.json()["items"]

    assert items[0]["application"] == "newer-app"
    assert items[1]["application"] == "older-app"