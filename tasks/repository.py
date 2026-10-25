"""Almacén en memoria del recurso `tasks`.

Sustituye a una base de datos real para que el proyecto sea ejecutable sin
infraestructura. Solo `service.py` usa este módulo.
"""
from datetime import date

from tasks.schemas import TaskOut

_tasks: dict[int, TaskOut] = {}
_task_id_by_idempotency_key: dict[str, int] = {}
_next_id: int = 1


def add(*, title: str, priority: int, due_date: date) -> TaskOut:
    """Guarda una tarea nueva con estado `"pending"` y le asigna un id.

    Args:
        title: Nombre de la tarea.
        priority: Urgencia, del 1 al 5.
        due_date: Fecha límite.

    Returns:
        La tarea guardada.
    """
    global _next_id
    task = TaskOut(
        id=_next_id,
        title=title,
        priority=priority,
        due_date=due_date,
        status="pending",
    )
    _tasks[task.id] = task
    _next_id += 1
    return task


def get(task_id: int) -> TaskOut | None:
    """Busca una tarea por id.

    Args:
        task_id: Identificador de la tarea.

    Returns:
        La tarea, o `None` si no existe.
    """
    return _tasks.get(task_id)


def find_by_idempotency_key(idempotency_key: str) -> TaskOut | None:
    """Busca la tarea creada previamente con una `Idempotency-Key`.

    Args:
        idempotency_key: Valor del header `Idempotency-Key`.

    Returns:
        La tarea asociada a la clave, o `None` si la clave no se ha usado.
    """
    task_id = _task_id_by_idempotency_key.get(idempotency_key)
    if task_id is None:
        return None
    return _tasks.get(task_id)


def save_idempotency_key(idempotency_key: str, task_id: int) -> None:
    """Asocia una `Idempotency-Key` con la tarea que creó.

    Args:
        idempotency_key: Valor del header `Idempotency-Key`.
        task_id: Identificador de la tarea creada.
    """
    _task_id_by_idempotency_key[idempotency_key] = task_id


def reset() -> None:
    """Vacía el almacén y reinicia los ids. Se usa entre tests."""
    global _next_id
    _tasks.clear()
    _task_id_by_idempotency_key.clear()
    _next_id = 1
