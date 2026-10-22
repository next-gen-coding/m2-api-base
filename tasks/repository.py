"""Almacén en memoria del recurso `tasks`.

Sustituye a una base de datos real para que el proyecto sea ejecutable sin
infraestructura. La API pública de este módulo imita la de un repositorio
real: la capa de `service.py` no debería notar la diferencia.
"""
from datetime import date, datetime, timezone

from tasks.schemas import Task

_tasks: dict[int, Task] = {}
_next_id: int = 1


def add(
    *,
    title: str,
    description: str | None,
    priority: int,
    user_id: int,
    due_date: date,
) -> Task:
    """Crea y almacena una tarea con id auto-incremental, status='todo' y created_at=utcnow."""
    global _next_id
    task = Task(
        id=_next_id,
        title=title,
        description=description,
        priority=priority,
        user_id=user_id,
        due_date=due_date,
        status="todo",
        created_at=datetime.now(timezone.utc),
    )
    _tasks[task.id] = task
    _next_id += 1
    return task


def get(task_id: int) -> Task | None:
    """Devuelve la tarea o None si no existe."""
    return _tasks.get(task_id)


def list_all() -> list[Task]:
    """Devuelve todas las tareas."""
    return list(_tasks.values())


def delete(task_id: int) -> bool:
    """Elimina una tarea. Devuelve True si existía, False si no."""
    return _tasks.pop(task_id, None) is not None


def update(task_id: int, **fields) -> Task | None:
    """Actualiza campos de una tarea existente. Devuelve None si no existe."""
    task = _tasks.get(task_id)
    if task is None:
        return None
    updated = task.model_copy(update=fields)
    _tasks[task_id] = updated
    return updated


def reset() -> None:
    """Limpia el almacén. Se usa entre tests."""
    global _next_id
    _tasks.clear()
    _next_id = 1


reset()
