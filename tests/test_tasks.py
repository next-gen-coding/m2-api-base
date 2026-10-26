"""Tests del recurso `tasks` (criterios CA1–CA6 de `docs/spec-tasks.md`).

Mismo estilo que `test_users.py`: un test por caso, nombre descriptivo en
español y arrange / act / assert separados por una línea en blanco.
"Hoy" se fija en `TODAY` sobrescribiendo la dependencia `get_today`.
"""
from datetime import date

import pytest
from fastapi.testclient import TestClient

from main import app
from tasks.routes import get_today

TODAY = date(2026, 10, 24)

VALID_PAYLOAD = {
    "title": "Revisar respaldo nocturno",
    "priority": 4,
    "due_date": "2026-11-15",
}


@pytest.fixture(autouse=True)
def _fixed_today():
    app.dependency_overrides[get_today] = lambda: TODAY
    yield
    app.dependency_overrides.pop(get_today, None)


def test_create_task_valida_devuelve_201_con_status_pending(client: TestClient) -> None:
    payload = dict(VALID_PAYLOAD)

    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "title": "Revisar respaldo nocturno",
        "priority": 4,
        "due_date": "2026-11-15",
        "status": "pending",
    }


@pytest.mark.parametrize(
    "title",
    ["", "   ", "ab", "a" * 101],
    ids=["vacio", "solo_espacios", "menos_de_3", "mas_de_100"],
)
def test_create_task_titulo_invalido_devuelve_422_y_no_crea_nada(
    client: TestClient, title: str
) -> None:
    payload = {**VALID_PAYLOAD, "title": title}

    response = client.post("/tasks", json=payload)

    assert response.status_code == 422
    assert client.get("/tasks/1").status_code == 404


@pytest.mark.parametrize(
    "priority",
    [0, 6, "alta"],
    ids=["cero", "seis", "no_numerica"],
)
def test_create_task_prioridad_fuera_de_rango_devuelve_422(
    client: TestClient, priority: object
) -> None:
    payload = {**VALID_PAYLOAD, "priority": priority}

    response = client.post("/tasks", json=payload)

    assert response.status_code == 422
    assert client.get("/tasks/1").status_code == 404


def test_create_task_fecha_pasada_devuelve_422_con_mensaje_en_espanol(
    client: TestClient,
) -> None:
    payload = {**VALID_PAYLOAD, "due_date": "2026-10-23"}

    response = client.post("/tasks", json=payload)

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "La fecha límite 2026-10-23 ya pasó; debe ser hoy o una fecha futura."
    )


def test_create_task_fecha_de_hoy_se_acepta(client: TestClient) -> None:
    payload = {**VALID_PAYLOAD, "due_date": TODAY.isoformat()}

    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    assert response.json()["due_date"] == "2026-10-24"


def test_create_task_misma_idempotency_key_devuelve_la_original_sin_duplicar(
    client: TestClient,
) -> None:
    headers = {"Idempotency-Key": "abc-123"}
    first = client.post("/tasks", json=VALID_PAYLOAD, headers=headers)

    second = client.post("/tasks", json=VALID_PAYLOAD, headers=headers)

    assert second.status_code == 201
    assert second.json() == first.json()
    assert second.json()["id"] == 1
    assert client.get("/tasks/2").status_code == 404


def test_get_task_existente_devuelve_200(client: TestClient) -> None:
    client.post("/tasks", json=VALID_PAYLOAD)

    response = client.get("/tasks/1")

    assert response.status_code == 200
    assert response.json()["title"] == "Revisar respaldo nocturno"


def test_get_task_inexistente_devuelve_404_con_mensaje_en_espanol(
    client: TestClient,
) -> None:
    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "tarea no encontrado: 999"


def test_crear_y_consultar_tarea_devuelve_los_mismos_datos(client: TestClient) -> None:
    created = client.post("/tasks", json=VALID_PAYLOAD).json()

    response = client.get(f"/tasks/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created
