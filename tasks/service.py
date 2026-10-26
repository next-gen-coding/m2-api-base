"""Lógica de negocio del recurso `tasks`.

Las rutas no acceden al repositorio directamente: pasan por aquí. Esta capa es la
única que conoce `repository.py` y la que decide cuándo algo es un error de
dominio (usando `core.errors`).

La fecha de "hoy" llega como parámetro (`today`) para poder simularla en tests;
no se llama a `date.today()` dentro de esta capa.
"""
from datetime import date

from core import errors
from tasks import repository
from tasks.schemas import TaskCreate, TaskOut


def create_task(
    data: TaskCreate,
    *,
    today: date,
    idempotency_key: str | None = None,
) -> TaskOut:
    """Crea una tarea, o devuelve la original si la clave de idempotencia ya se usó.

    Args:
        data: Datos de la tarea, ya validados en formato por `TaskCreate`.
        today: Fecha de hoy, inyectada por la ruta.
        idempotency_key: Valor del header `Idempotency-Key`, si vino.

    Returns:
        La tarea creada, o la tarea original si la clave ya existía. Con una clave
        ya usada no se compara el cuerpo ni se revalida la fecha: se devuelve la
        original tal cual.

    Raises:
        HTTPException: 422 (`errors.invalid_request`) si `due_date` es anterior a
            `today` y la clave no se había usado antes.

    Example:
        >>> data = TaskCreate(title="Revisar respaldo", priority=4, due_date=date(2026, 11, 15))
        >>> create_task(data, today=date(2026, 10, 24)).status
        'pending'
    """
    if idempotency_key is not None:
        original = repository.find_by_idempotency_key(idempotency_key)
        if original is not None:
            return original
    if data.due_date < today:
        raise errors.invalid_request(
            f"La fecha límite {data.due_date.isoformat()} ya pasó; "
            "debe ser hoy o una fecha futura."
        )
    task = repository.add(
        title=data.title,
        priority=data.priority,
        due_date=data.due_date,
    )
    if idempotency_key is not None:
        repository.save_idempotency_key(idempotency_key, task.id)
    return task


def get_task(task_id: int) -> TaskOut:
    """Devuelve una tarea por id.

    Args:
        task_id: Identificador de la tarea.

    Returns:
        La tarea encontrada.

    Raises:
        HTTPException: 404 (`errors.not_found`) si la tarea no existe.

    Example:
        >>> data = TaskCreate(title="Revisar respaldo", priority=4, due_date=date(2026, 11, 15))
        >>> created = create_task(data, today=date(2026, 10, 24))
        >>> get_task(created.id) == created
        True
    """
    task = repository.get(task_id)
    if task is None:
        raise errors.not_found("tarea", task_id)
    return task
