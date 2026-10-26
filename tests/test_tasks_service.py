"""Tests unitarios de `tasks/service.py`, sin TestClient.

`tasks.repository` se sustituye por un mock con la misma firma (`create_autospec`)
para comprobar con qué datos lo llama el service. `today` se pasa como fecha fija.
"""
from datetime import date
from unittest.mock import MagicMock, create_autospec

import pytest
from fastapi import HTTPException

from tasks import repository, service
from tasks.schemas import TaskCreate, TaskOut

TODAY = date(2026, 10, 24)


@pytest.fixture
def repository_mock(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock = create_autospec(repository, spec_set=True)
    monkeypatch.setattr(service, "repository", mock)
    return mock


def make_data(due_date: date = date(2026, 11, 15)) -> TaskCreate:
    return TaskCreate(title="Revisar respaldo nocturno", priority=4, due_date=due_date)


def make_task(task_id: int = 1, due_date: date = date(2026, 11, 15)) -> TaskOut:
    return TaskOut(
        id=task_id,
        title="Revisar respaldo nocturno",
        priority=4,
        due_date=due_date,
        status="pending",
    )


def test_create_task_sin_clave_llama_a_add_con_los_datos_y_devuelve_la_tarea(
    repository_mock: MagicMock,
) -> None:
    # Arrange
    created = make_task()
    repository_mock.add.return_value = created

    # Act
    result = service.create_task(make_data(), today=TODAY)

    # Assert
    assert result is created
    repository_mock.add.assert_called_once_with(
        title="Revisar respaldo nocturno", priority=4, due_date=date(2026, 11, 15)
    )
    repository_mock.find_by_idempotency_key.assert_not_called()
    repository_mock.save_idempotency_key.assert_not_called()


def test_create_task_con_clave_nueva_crea_y_registra_la_clave(
    repository_mock: MagicMock,
) -> None:
    # Arrange
    repository_mock.find_by_idempotency_key.return_value = None
    repository_mock.add.return_value = make_task(task_id=7)

    # Act
    result = service.create_task(make_data(), today=TODAY, idempotency_key="abc-123")

    # Assert
    assert result.id == 7
    repository_mock.find_by_idempotency_key.assert_called_once_with("abc-123")
    repository_mock.add.assert_called_once()
    repository_mock.save_idempotency_key.assert_called_once_with("abc-123", 7)


def test_create_task_con_clave_repetida_devuelve_la_original_y_no_llama_a_add(
    repository_mock: MagicMock,
) -> None:
    # Arrange
    original = make_task(task_id=3)
    repository_mock.find_by_idempotency_key.return_value = original

    # Act
    result = service.create_task(make_data(), today=TODAY, idempotency_key="abc-123")

    # Assert
    assert result is original
    repository_mock.find_by_idempotency_key.assert_called_once_with("abc-123")
    repository_mock.add.assert_not_called()
    repository_mock.save_idempotency_key.assert_not_called()


def test_create_task_fecha_pasada_levanta_422_y_no_llama_a_add(
    repository_mock: MagicMock,
) -> None:
    # Arrange
    data = make_data(due_date=date(2026, 10, 23))

    # Act
    with pytest.raises(HTTPException) as error:
        service.create_task(data, today=TODAY)

    # Assert
    assert error.value.status_code == 422
    assert error.value.detail == (
        "La fecha límite 2026-10-23 ya pasó; debe ser hoy o una fecha futura."
    )
    repository_mock.add.assert_not_called()


def test_create_task_fecha_de_hoy_se_acepta_y_llama_a_add(
    repository_mock: MagicMock,
) -> None:
    # Arrange
    repository_mock.add.return_value = make_task(due_date=TODAY)

    # Act
    result = service.create_task(make_data(due_date=TODAY), today=TODAY)

    # Assert
    assert result.due_date == TODAY
    repository_mock.add.assert_called_once_with(
        title="Revisar respaldo nocturno", priority=4, due_date=TODAY
    )


def test_create_task_clave_repetida_con_fecha_pasada_devuelve_la_original_sin_validar(
    repository_mock: MagicMock,
) -> None:
    # Arrange
    original = make_task(task_id=3)
    repository_mock.find_by_idempotency_key.return_value = original
    data = make_data(due_date=date(2026, 10, 1))

    # Act
    result = service.create_task(data, today=TODAY, idempotency_key="abc-123")

    # Assert
    assert result is original
    repository_mock.add.assert_not_called()


def test_get_task_existente_devuelve_la_tarea_del_repositorio(
    repository_mock: MagicMock,
) -> None:
    # Arrange
    task = make_task(task_id=5)
    repository_mock.get.return_value = task

    # Act
    result = service.get_task(5)

    # Assert
    assert result is task
    repository_mock.get.assert_called_once_with(5)


def test_get_task_inexistente_levanta_404_con_mensaje_en_espanol(
    repository_mock: MagicMock,
) -> None:
    # Arrange
    repository_mock.get.return_value = None

    # Act
    with pytest.raises(HTTPException) as error:
        service.get_task(999)

    # Assert
    assert error.value.status_code == 404
    assert error.value.detail == "tarea no encontrado: 999"
    repository_mock.get.assert_called_once_with(999)
