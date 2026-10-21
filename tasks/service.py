"""Lógica de negocio del recurso `tasks`.

Las rutas no acceden al repositorio directamente: pasan por aquí. Esta capa es la
única que conoce `repository.py` y la que decide cuándo algo es un error de
dominio (usando `core.errors`).
"""
from datetime import date

from core import errors
from tasks import repository
from tasks.schemas import Task, TaskCreate


def create_task(data: TaskCreate) -> Task:
    if data.due_date is not None and data.due_date < date.today():
        raise errors.invalid_request("La fecha límite no puede estar en el pasado")
    return repository.add(
        title=data.title,
        description=data.description,
        priority=data.priority,
        due_date=data.due_date,
    )
