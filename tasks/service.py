"""Lógica de negocio del recurso `tasks`.

Las rutas no acceden al repositorio directamente: pasan por aquí. Esta capa es la
única que conoce `repository.py` y la que decide cuándo algo es un error de
dominio (usando `core.errors`).

La fecha de "hoy" llega como parámetro (`today`) para poder simularla en tests;
no se llama a `date.today()` dentro de esta capa.
"""
from datetime import date

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
        La tarea creada, o la tarea original si la clave ya existía.

    Raises:
        HTTPException: 422 (`errors.invalid_request`) si `due_date` es anterior a `today`.

    Example:
        >>> data = TaskCreate(title="Revisar respaldo", priority=4, due_date=date(2026, 11, 15))
        >>> create_task(data, today=date(2026, 10, 24)).status
        'pending'
    """
    # TODO: idempotencia — si `idempotency_key` ya existe en el repositorio,
    #       devolver la tarea original sin crear otra.
    # TODO: fecha pasada — si `data.due_date < today`, levantar
    #       `errors.invalid_request` con mensaje en español (hoy sí se acepta).
    # TODO: si vino clave, registrarla con `repository.save_idempotency_key(...)`.
    return repository.add(
        title=data.title,
        priority=data.priority,
        due_date=data.due_date,
    )


def get_task(task_id: int) -> TaskOut:
    """Devuelve una tarea por id.

    Args:
        task_id: Identificador de la tarea.

    Returns:
        La tarea encontrada.

    Raises:
        HTTPException: 404 (`errors.not_found`) si la tarea no existe.

    Example:
        >>> get_task(1).id
        1
    """
    # TODO: no encontrado — si `repository.get(task_id)` es `None`, levantar
    #       `errors.not_found("tarea", task_id)`.
    return repository.get(task_id)
