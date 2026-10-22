"""Tests del recurso `tasks`.

Naming: test_CANN_<descripción> donde NN es el número de criterio de aceptación.
Estilo: arrange / act / assert separados por una línea en blanco.
"""
from datetime import date, datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from tasks import service as tasks_service
from tasks.schemas import Task, TaskCreate, TaskUpdate


def _fecha_futura() -> str:
    return (date.today() + timedelta(days=7)).isoformat()


def _fecha_pasada() -> str:
    return (date.today() - timedelta(days=1)).isoformat()


def _payload(**overrides) -> dict:
    base = {
        "title": "Tarea de ejemplo",
        "description": "Descripción de prueba",
        "priority": 3,
        "user_id": 1,
        "due_date": _fecha_futura(),
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# CA01 — POST /tasks/ crea la tarea asignada a un usuario (201)
# ---------------------------------------------------------------------------


def test_CA01_crear_tarea_devuelve_201(client: TestClient) -> None:
    response = client.post("/tasks", json=_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["title"] == "Tarea de ejemplo"
    assert body["user_id"] == 1


# ---------------------------------------------------------------------------
# CA02 — GET /tasks/{task_id} retorna una tarea (200)
# ---------------------------------------------------------------------------


def test_CA02_obtener_tarea_existente_devuelve_200(client: TestClient) -> None:
    client.post("/tasks", json=_payload())

    response = client.get("/tasks/1")

    assert response.status_code == 200
    assert response.json()["title"] == "Tarea de ejemplo"


# ---------------------------------------------------------------------------
# CA03 — GET /tasks/ retorna la lista de tareas existentes (200)
# ---------------------------------------------------------------------------


def test_CA03_listar_tareas_vacia_devuelve_lista_vacia(client: TestClient) -> None:
    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []


def test_CA03_listar_tareas_devuelve_las_creadas(client: TestClient) -> None:
    client.post("/tasks", json=_payload())
    client.post("/tasks", json=_payload(title="Segunda tarea"))

    response = client.get("/tasks")

    assert response.status_code == 200
    assert len(response.json()) == 2


# ---------------------------------------------------------------------------
# CA04 — Error 404 si el usuario asignado no existe al crear la tarea
# ---------------------------------------------------------------------------


def test_CA04_crear_tarea_usuario_inexistente_devuelve_404(client: TestClient) -> None:
    response = client.post("/tasks", json=_payload(user_id=999))

    assert response.status_code == 404
    assert "no encontrado" in response.json()["detail"]


# ---------------------------------------------------------------------------
# CA05 — DELETE /tasks/{task_id} permite eliminar una tarea (204)
# ---------------------------------------------------------------------------


def test_CA05_eliminar_tarea_existente_devuelve_204(client: TestClient) -> None:
    client.post("/tasks", json=_payload())

    response = client.delete("/tasks/1")

    assert response.status_code == 204


# ---------------------------------------------------------------------------
# CA06 — PATCH solo puede cambiar user_id y/o status
# ---------------------------------------------------------------------------


def test_CA06_actualizar_status_devuelve_200(client: TestClient) -> None:
    client.post("/tasks", json=_payload())

    response = client.patch("/tasks/1", json={"status": "in_progress"})

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_CA06_actualizar_user_id_devuelve_200(client: TestClient) -> None:
    client.post("/tasks", json=_payload(user_id=1))

    response = client.patch("/tasks/1", json={"user_id": 2})

    assert response.status_code == 200
    assert response.json()["user_id"] == 2


# ---------------------------------------------------------------------------
# CA07 — Status permitidos: todo, in_progress, done. Transiciones libres.
# ---------------------------------------------------------------------------


def test_CA07_transicion_todo_a_done(client: TestClient) -> None:
    client.post("/tasks", json=_payload())

    response = client.patch("/tasks/1", json={"status": "done"})

    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_CA07_transicion_done_a_todo(client: TestClient) -> None:
    client.post("/tasks", json=_payload())
    client.patch("/tasks/1", json={"status": "done"})

    response = client.patch("/tasks/1", json={"status": "todo"})

    assert response.status_code == 200
    assert response.json()["status"] == "todo"


def test_CA07_status_invalido_devuelve_422(client: TestClient) -> None:
    client.post("/tasks", json=_payload())

    response = client.patch("/tasks/1", json={"status": "cancelado"})

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# CA08 — El response regresa todos los campos
# ---------------------------------------------------------------------------


def test_CA08_response_contiene_todos_los_campos(client: TestClient) -> None:
    response = client.post("/tasks", json=_payload())

    body = response.json()
    campos_esperados = {
        "id", "title", "description", "priority",
        "status", "user_id", "due_date", "created_at",
    }

    assert campos_esperados == set(body.keys())


# ---------------------------------------------------------------------------
# CA09 — Status por default es todo; no se acepta en el POST
# ---------------------------------------------------------------------------


def test_CA09_status_default_es_todo(client: TestClient) -> None:
    response = client.post("/tasks", json=_payload())

    assert response.json()["status"] == "todo"


# ---------------------------------------------------------------------------
# CA10 — Consultar tarea inexistente regresa 404
# ---------------------------------------------------------------------------


def test_CA10_obtener_tarea_inexistente_devuelve_404(client: TestClient) -> None:
    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert "no encontrado" in response.json()["detail"]


# ---------------------------------------------------------------------------
# CA11 — Prioridad de 1 a 5; fuera de rango → 422
# ---------------------------------------------------------------------------


def test_CA11_prioridad_0_devuelve_422(client: TestClient) -> None:
    response = client.post("/tasks", json=_payload(priority=0))

    assert response.status_code == 422


def test_CA11_prioridad_6_devuelve_422(client: TestClient) -> None:
    response = client.post("/tasks", json=_payload(priority=6))

    assert response.status_code == 422


def test_CA11_prioridad_negativa_devuelve_422(client: TestClient) -> None:
    response = client.post("/tasks", json=_payload(priority=-1))

    assert response.status_code == 422


# Equivalence: prioridades válidas 1, 3, 5


def test_CA11_eq_prioridad_1_valida(client: TestClient) -> None:
    response = client.post("/tasks", json=_payload(priority=1))

    assert response.status_code == 201
    assert response.json()["priority"] == 1


def test_CA11_eq_prioridad_3_valida(client: TestClient) -> None:
    response = client.post("/tasks", json=_payload(priority=3))

    assert response.status_code == 201
    assert response.json()["priority"] == 3


def test_CA11_eq_prioridad_5_valida(client: TestClient) -> None:
    response = client.post("/tasks", json=_payload(priority=5))

    assert response.status_code == 201
    assert response.json()["priority"] == 5


# ---------------------------------------------------------------------------
# CA12 — Fecha en el pasado (o igual a hoy) → 422
# ---------------------------------------------------------------------------


def test_CA12_fecha_pasada_devuelve_422(client: TestClient) -> None:
    response = client.post("/tasks", json=_payload(due_date=_fecha_pasada()))

    assert response.status_code == 422


def test_CA12_fecha_hoy_devuelve_422(client: TestClient) -> None:
    response = client.post("/tasks", json=_payload(due_date=date.today().isoformat()))

    assert response.status_code == 422


def test_CA12_fecha_manana_es_valida(client: TestClient) -> None:
    manana = (date.today() + timedelta(days=1)).isoformat()

    response = client.post("/tasks", json=_payload(due_date=manana))

    assert response.status_code == 201


# Edge: formato de fecha inválido


def test_CA12_edge_fecha_formato_invalido_devuelve_422(client: TestClient) -> None:
    response = client.post("/tasks", json=_payload(due_date="no-es-fecha"))

    assert response.status_code == 422


def test_CA12_edge_fecha_null_devuelve_422(client: TestClient) -> None:
    response = client.post("/tasks", json=_payload(due_date=None))

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# CA13 — Título de 1 a 120 caracteres
# ---------------------------------------------------------------------------


# Boundary: mínimo válido (1 char)


def test_CA13_boundary_titulo_1_caracter_valido(client: TestClient) -> None:
    response = client.post("/tasks", json=_payload(title="A"))

    assert response.status_code == 201
    assert response.json()["title"] == "A"


# Boundary: máximo válido (120 chars)


def test_CA13_boundary_titulo_120_caracteres_valido(client: TestClient) -> None:
    titulo = "x" * 120

    response = client.post("/tasks", json=_payload(title=titulo))

    assert response.status_code == 201
    assert len(response.json()["title"]) == 120


# Boundary: justo fuera (0 y 121)


def test_CA13_boundary_titulo_vacio_devuelve_422(client: TestClient) -> None:
    response = client.post("/tasks", json=_payload(title=""))

    assert response.status_code == 422


def test_CA13_boundary_titulo_121_caracteres_devuelve_422(client: TestClient) -> None:
    response = client.post("/tasks", json=_payload(title="x" * 121))

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# CA14 — description opcional, máximo 500 caracteres
# ---------------------------------------------------------------------------


def test_CA14_descripcion_null_es_valida(client: TestClient) -> None:
    response = client.post("/tasks", json=_payload(description=None))

    assert response.status_code == 201
    assert response.json()["description"] is None


def test_CA14_descripcion_500_caracteres_valida(client: TestClient) -> None:
    response = client.post("/tasks", json=_payload(description="d" * 500))

    assert response.status_code == 201


def test_CA14_descripcion_501_caracteres_devuelve_422(client: TestClient) -> None:
    response = client.post("/tasks", json=_payload(description="d" * 501))

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# CA15 — DELETE de tarea inexistente regresa 404
# ---------------------------------------------------------------------------


def test_CA15_eliminar_tarea_inexistente_devuelve_404(client: TestClient) -> None:
    response = client.delete("/tasks/999")

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# CA16 — PATCH de tarea inexistente regresa 404
# ---------------------------------------------------------------------------


def test_CA16_actualizar_tarea_inexistente_devuelve_404(client: TestClient) -> None:
    response = client.patch("/tasks/999", json={"status": "done"})

    assert response.status_code == 404
    assert "no encontrado" in response.json()["detail"]


# ---------------------------------------------------------------------------
# CA17 — PATCH con user_id inexistente regresa 404
# ---------------------------------------------------------------------------


def test_CA17_patch_usuario_inexistente_devuelve_404(client: TestClient) -> None:
    client.post("/tasks", json=_payload())

    response = client.patch("/tasks/1", json={"user_id": 999})

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# CA18 — Mismas validaciones del POST aplican en el PATCH
# ---------------------------------------------------------------------------


def test_CA18_patch_status_invalido_aplica_validacion(client: TestClient) -> None:
    client.post("/tasks", json=_payload())

    response = client.patch("/tasks/1", json={"status": "invalido"})

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# CA19 — PATCH retorna 200 con la tarea actualizada completa
# ---------------------------------------------------------------------------


def test_CA19_patch_retorna_tarea_completa(client: TestClient) -> None:
    client.post("/tasks", json=_payload())

    response = client.patch("/tasks/1", json={"status": "done"})

    assert response.status_code == 200
    body = response.json()
    campos_esperados = {
        "id", "title", "description", "priority",
        "status", "user_id", "due_date", "created_at",
    }
    assert campos_esperados == set(body.keys())
    assert body["status"] == "done"


# ---------------------------------------------------------------------------
# CA20 — created_at es de tipo datetime
# ---------------------------------------------------------------------------


def test_CA20_created_at_es_datetime(client: TestClient) -> None:
    response = client.post("/tasks", json=_payload())

    created_at = response.json()["created_at"]
    assert "T" in created_at  # formato ISO datetime incluye 'T'


# ---------------------------------------------------------------------------
# CA21 — due_date es de tipo date (sin hora)
# ---------------------------------------------------------------------------


def test_CA21_due_date_es_date_sin_hora(client: TestClient) -> None:
    response = client.post("/tasks", json=_payload())

    due_date = response.json()["due_date"]
    assert "T" not in due_date  # formato ISO date NO incluye 'T'


# ---------------------------------------------------------------------------
# CA22 — Idempotencia
# ---------------------------------------------------------------------------


def test_CA22_patch_repetido_es_idempotente(client: TestClient) -> None:
    client.post("/tasks", json=_payload())
    client.patch("/tasks/1", json={"status": "done"})

    response = client.patch("/tasks/1", json={"status": "done"})

    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_CA22_delete_repetido_204_luego_404(client: TestClient) -> None:
    client.post("/tasks", json=_payload())

    primera = client.delete("/tasks/1")
    segunda = client.delete("/tasks/1")

    assert primera.status_code == 204
    assert segunda.status_code == 404


# ---------------------------------------------------------------------------
# Edge cases adicionales
# ---------------------------------------------------------------------------


def test_edge_patch_body_vacio_no_modifica(client: TestClient) -> None:
    client.post("/tasks", json=_payload())

    response = client.patch("/tasks/1", json={})

    assert response.status_code == 200
    assert response.json()["status"] == "todo"


def test_edge_eliminar_tarea_ya_no_es_accesible(client: TestClient) -> None:
    client.post("/tasks", json=_payload())
    client.delete("/tasks/1")

    response = client.get("/tasks/1")

    assert response.status_code == 404


def test_edge_crear_sin_campo_obligatorio_devuelve_422(client: TestClient) -> None:
    payload = {"title": "Sin user_id", "priority": 3, "due_date": _fecha_futura()}

    response = client.post("/tasks", json=payload)

    assert response.status_code == 422


def test_edge_titulo_solo_espacios_devuelve_422(client: TestClient) -> None:
    response = client.post("/tasks", json=_payload(title="   "))

    assert response.status_code == 422


# ===========================================================================
# Tests unitarios de service
# ===========================================================================
# Llaman directamente a las funciones de tasks/service.py usando mocks
# para aislar la unidad bajo prueba.

def _dummy_task(**overrides) -> Task:
    """Construye un Task válido para usar como retorno de mocks."""
    defaults = {
        "id": 1,
        "title": "Tarea mock",
        "description": None,
        "priority": 3,
        "user_id": 1,
        "due_date": date.today() + timedelta(days=7),
        "status": "todo",
        "created_at": datetime.now(timezone.utc),
    }
    defaults.update(overrides)
    return Task(**defaults)


@patch("tasks.service.repository")
@patch("tasks.service.users_service")
def test_unit_create_task_llama_a_users_service(
    mock_users_svc: MagicMock, mock_repo: MagicMock
) -> None:
    mock_users_svc.get_user.return_value = True
    mock_repo.add.return_value = _dummy_task()
    data = TaskCreate(
        title="Test", priority=3, user_id=1,
        due_date=date.today() + timedelta(days=7),
    )

    tasks_service.create_task(data)

    mock_users_svc.get_user.assert_called_once_with(1)
    mock_repo.add.assert_called_once()


@patch("tasks.service.repository")
@patch("tasks.service.users_service")
def test_unit_create_task_usuario_inexistente_no_llama_repo_add(
    mock_users_svc: MagicMock, mock_repo: MagicMock
) -> None:
    mock_users_svc.get_user.side_effect = HTTPException(status_code=404, detail="no encontrado")
    data = TaskCreate(
        title="Test", priority=3, user_id=999,
        due_date=date.today() + timedelta(days=7),
    )

    try:
        tasks_service.create_task(data)
    except HTTPException:
        pass

    mock_repo.add.assert_not_called()


@patch("tasks.service.repository")
@patch("tasks.service.users_service")
def test_unit_update_task_valida_status(
    mock_users_svc: MagicMock, mock_repo: MagicMock
) -> None:
    mock_repo.get.return_value = _dummy_task()
    data = TaskUpdate(status="invalido")

    try:
        tasks_service.update_task(1, data)
    except HTTPException as exc:
        assert exc.status_code == 422

    mock_repo.update.assert_not_called()


@patch("tasks.service.repository")
@patch("tasks.service.users_service")
def test_unit_update_task_valida_user_id_existente(
    mock_users_svc: MagicMock, mock_repo: MagicMock
) -> None:
    mock_repo.get.return_value = _dummy_task()
    mock_repo.update.return_value = _dummy_task(user_id=2)
    mock_users_svc.get_user.return_value = True
    data = TaskUpdate(user_id=2)

    tasks_service.update_task(1, data)

    mock_users_svc.get_user.assert_called_once_with(2)
    mock_repo.update.assert_called_once()


def test_unit_due_date_igual_a_hoy_da_error(monkeypatch: pytest.MonkeyPatch) -> None:
    fecha_fija = date(2026, 6, 15)
    monkeypatch.setattr(tasks_service, "today", lambda: fecha_fija)

    data = TaskCreate(
        title="Test", priority=3, user_id=1, due_date=fecha_fija,
    )

    with pytest.raises(HTTPException) as exc_info:
        tasks_service.create_task(data)

    assert exc_info.value.status_code == 422


# ===========================================================================
# Tests de integración
# ===========================================================================
# Flujo completo pasando por HTTP: crear usuario, asignar tarea, reasignar,
# verificar.


def test_integracion_crear_usuario_asignar_tarea_y_reasignar(
    client: TestClient,
) -> None:
    # arrange — crear dos usuarios nuevos vía la API
    user_a = client.post(
        "/users", json={"name": "Usuario A", "email": "a@test.com"}
    ).json()
    user_b = client.post(
        "/users", json={"name": "Usuario B", "email": "b@test.com"}
    ).json()

    # act — crear tarea asignada a usuario A
    tarea = client.post("/tasks", json=_payload(user_id=user_a["id"])).json()
    assert tarea["user_id"] == user_a["id"]

    # act — reasignar la tarea a usuario B vía PATCH
    patch_resp = client.patch(
        f"/tasks/{tarea['id']}", json={"user_id": user_b["id"]}
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["user_id"] == user_b["id"]

    # assert — verificar con GET que la reasignación persiste
    get_resp = client.get(f"/tasks/{tarea['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["user_id"] == user_b["id"]


def test_integracion_crear_tarea_cambiar_status_y_verificar(
    client: TestClient,
) -> None:
    # arrange
    tarea = client.post("/tasks", json=_payload()).json()

    # act — transicionar status
    client.patch(f"/tasks/{tarea['id']}", json={"status": "in_progress"})
    resp_done = client.patch(f"/tasks/{tarea['id']}", json={"status": "done"})

    # assert
    assert resp_done.status_code == 200
    get_resp = client.get(f"/tasks/{tarea['id']}")
    assert get_resp.json()["status"] == "done"
