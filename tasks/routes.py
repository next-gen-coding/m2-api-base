"""Rutas HTTP del recurso `tasks`.

Mismo patrón que `users/routes.py`: `response_model=` siempre y la función
delega en `service.py` sin lógica de negocio.
"""
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Header, status

from tasks import service
from tasks.schemas import TaskCreate, TaskOut

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_today() -> date:
    """Dependencia que provee la fecha de hoy; en tests se sobrescribe.

    Returns:
        La fecha actual.
    """
    return date.today()


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreate,
    today: Annotated[date, Depends(get_today)],
    idempotency_key: Annotated[str | None, Header()] = None,
) -> TaskOut:
    """Crea una tarea (`POST /tasks`).

    Args:
        data: Cuerpo de la petición.
        today: Fecha de hoy, inyectada con `get_today`.
        idempotency_key: Header opcional `Idempotency-Key`.

    Returns:
        La tarea creada (o la original, si la clave ya se usó).
    """
    return service.create_task(data, today=today, idempotency_key=idempotency_key)


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int) -> TaskOut:
    """Consulta una tarea (`GET /tasks/{task_id}`).

    Args:
        task_id: Identificador de la tarea.

    Returns:
        La tarea encontrada.
    """
    return service.get_task(task_id)
