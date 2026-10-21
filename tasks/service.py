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
    """Crea una tarea tras validar que su fecha límite no esté en el pasado.

    Una `due_date` igual a la fecha de referencia es válida; solo se rechazan las
    anteriores. Si `data.due_date` es `None`, no se valida ninguna fecha.

    Args:
        data: Datos de entrada ya validados por Pydantic (título, descripción,
            prioridad y fecha límite opcional).
        current_date: Fecha de referencia para la comparación. Si es `None`, se
            usa la fecha actual en UTC (coherente con `created_at`).

    Returns:
        La `Task` persistida, con `id` autoincremental y `created_at` en UTC.

    Raises:
        HTTPException: 422 (vía `errors.invalid_request`) si `data.due_date` es
            anterior a la fecha de referencia.
    """
    reference_date = current_date or datetime.now(timezone.utc).date()
    if data.due_date is not None and data.due_date < reference_date:
        raise errors.invalid_request("La fecha límite no puede estar en el pasado")
    return repository.add(
        title=data.title,
        description=data.description,
        priority=data.priority,
        due_date=data.due_date,
    )
