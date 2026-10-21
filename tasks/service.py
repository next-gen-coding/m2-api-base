"""Lógica de negocio del recurso `tasks`.

Las rutas no acceden al repositorio directamente: pasan por aquí. Esta capa es la
única que conoce `repository.py` y la que decide cuándo algo es un error de
dominio (usando `core.errors`).
"""
from datetime import date, datetime, timezone

from core import errors
from tasks import repository
from tasks.schemas import Task, TaskCreate


def create_task(data: TaskCreate, current_date: date | None = None) -> Task:
    reference_date = current_date or datetime.now(timezone.utc).date()
    if data.due_date is not None and data.due_date < reference_date:
        raise errors.invalid_request("La fecha límite no puede estar en el pasado")
    return repository.add(
        title=data.title,
        description=data.description,
        priority=data.priority,
        due_date=data.due_date,
    )
