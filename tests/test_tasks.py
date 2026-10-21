"""Tests del recurso `tasks`."""
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from tasks import repository


def test_create_task_success(client: TestClient) -> None:
    due_date = date.today() + timedelta(days=7)
    payload = {
        "title": "Write report",
        "description": "Quarterly summary",
        "priority": "medium",
        "due_date": due_date.isoformat(),
    }

    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["title"] == "Write report"
    assert body["description"] == "Quarterly summary"
    assert body["priority"] == "medium"
    assert body["due_date"] == due_date.isoformat()
    assert "created_at" in body


def test_create_task_without_optional_fields_uses_defaults(client: TestClient) -> None:
    payload = {"title": "Minimal task"}

    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["description"] is None
    assert body["priority"] == "medium"
    assert body["due_date"] is None


def test_create_task_today_as_due_date_is_valid(client: TestClient) -> None:
    payload = {"title": "Due today", "due_date": date.today().isoformat()}

    response = client.post("/tasks", json=payload)

    assert response.status_code == 201


@pytest.mark.parametrize("payload", [{"title": ""}, {"description": "No title"}])
def test_create_task_invalid_title(client: TestClient, payload: dict) -> None:
    response = client.post("/tasks", json=payload)

    assert response.status_code == 422
    assert any(error["loc"][-1] == "title" for error in response.json()["detail"])
    assert repository.list_all() == []


@pytest.mark.parametrize("priority", ["media", "urgent", "", 1])
def test_create_task_invalid_priority(client: TestClient, priority: object) -> None:
    payload = {"title": "Bad priority", "priority": priority}

    response = client.post("/tasks", json=payload)

    assert response.status_code == 422
    assert any(error["loc"][-1] == "priority" for error in response.json()["detail"])
    assert repository.list_all() == []


def test_create_task_past_due_date(client: TestClient) -> None:
    yesterday = date.today() - timedelta(days=1)
    payload = {"title": "Late task", "due_date": yesterday.isoformat()}

    response = client.post("/tasks", json=payload)

    # `errors.invalid_request` responde 422 (no 400).
    assert response.status_code == 422
    assert response.json()["detail"] == "La fecha límite no puede estar en el pasado"
    assert repository.list_all() == []


def test_create_task_integration_flow(client: TestClient) -> None:
    first = client.post("/tasks", json={"title": "First", "priority": "high"})
    second = client.post("/tasks", json={"title": "Second", "priority": "low"})

    assert first.status_code == 201
    assert second.status_code == 201
    assert [first.json()["id"], second.json()["id"]] == [1, 2]
    stored = repository.list_all()
    assert [task.title for task in stored] == ["First", "Second"]
    assert repository.get(2) is not None
    assert repository.get(2).priority == "low"
