"""Almacén en memoria del recurso `tasks`.

Sustituye a una base de datos real para que el proyecto sea ejecutable sin
infraestructura. La API pública de este módulo (las funciones de abajo) imita la
de un repositorio real: la capa de `service.py` no debería notar la diferencia.
"""
from datetime import date, datetime, timezone

from tasks.schemas import Task, TaskPriority

_tasks: dict[int, Task] = {}
_next_id: int = 1


def add(
    *,
    title: str,
    description: str | None,
    priority: TaskPriority,
    due_date: date | None,
) -> Task:
    global _next_id
    task = Task(
        id=_next_id,
        title=title,
        description=description,
        priority=priority,
        due_date=due_date,
        created_at=datetime.now(timezone.utc),
    )
    _tasks[task.id] = task
    _next_id += 1
    return task


def get(task_id: int) -> Task | None:
    return _tasks.get(task_id)


def list_all() -> list[Task]:
    return list(_tasks.values())


def reset() -> None:
    """Deja el almacén vacío. Se usa entre tests."""
    global _next_id
    _tasks.clear()
    _next_id = 1


reset()
