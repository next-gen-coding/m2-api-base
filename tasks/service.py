"""Lógica de negocio del recurso `tasks`.

Las rutas no acceden al repositorio directamente: pasan por aquí. Esta capa es la
única que conoce `repository.py` y la que decide cuándo algo es un error de
dominio (usando `core.errors`).
"""
from datetime import date

from core import errors
from tasks import repository
from tasks.schemas import Task, TaskCreate, TaskUpdate
from users import service as users_service

_VALID_STATUSES = {"todo", "in_progress", "done"}


def today() -> date:
    """Retorna la fecha actual. Extraída para facilitar su sustitución en tests."""
    return date.today()


def _validate_due_date(due_date: date) -> None:
    """Rechaza fechas que no sean estrictamente futuras."""
    if due_date <= today():
        raise errors.invalid_request("La fecha límite debe ser posterior a hoy")


def _validate_user_exists(user_id: int) -> None:
    """Delega en users.service.get_user(); levanta 404 si no existe."""
    users_service.get_user(user_id)


def _validate_status(status: str) -> None:
    """Rechaza valores fuera de _VALID_STATUSES con 422."""
    if status not in _VALID_STATUSES:
        raise errors.invalid_request(
            f"Estado inválido: {status}. Valores permitidos: todo, in_progress, done"
        )


def create_task(data: TaskCreate) -> Task:
    """Valida due_date y user_id, crea la tarea con status 'todo'."""
    _validate_due_date(data.due_date)
    _validate_user_exists(data.user_id)
    return repository.add(
        title=data.title,
        description=data.description,
        priority=data.priority,
        user_id=data.user_id,
        due_date=data.due_date,
    )


def get_task(task_id: int) -> Task:
    """Retorna la tarea o levanta not_found('tarea', task_id)."""
    task = repository.get(task_id)
    if task is None:
        raise errors.not_found("tarea", task_id)
    return task


def list_tasks() -> list[Task]:
    """Retorna todas las tareas."""
    return repository.list_all()


def delete_task(task_id: int) -> None:
    """Elimina la tarea o levanta not_found('tarea', task_id)."""
    if not repository.delete(task_id):
        raise errors.not_found("tarea", task_id)


def update_task(task_id: int, data: TaskUpdate) -> Task:
    """Valida existencia de tarea, valida status y/o user_id si vienen, actualiza."""
    task = repository.get(task_id)
    if task is None:
        raise errors.not_found("tarea", task_id)

    fields: dict = {}

    if data.status is not None:
        _validate_status(data.status)
        fields["status"] = data.status

    if data.user_id is not None:
        _validate_user_exists(data.user_id)
        fields["user_id"] = data.user_id

    if not fields:
        return task

    updated = repository.update(task_id, **fields)
    assert updated is not None
    return updated
