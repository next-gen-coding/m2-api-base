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
    """Guarda una nueva tarea en memoria.

    No valida nada: las reglas de negocio viven en `service.py`.

    Args:
        title: Título de la tarea.
        description: Descripción opcional.
        priority: Prioridad de la tarea.
        due_date: Fecha límite opcional.

    Returns:
        La `Task` almacenada, con `id` autoincremental (desde 1) y `created_at`
        en UTC.
    """
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
    """Busca una tarea por identificador.

    Args:
        task_id: Identificador de la tarea.

    Returns:
        La `Task` encontrada, o `None` si no existe.
    """
    return _tasks.get(task_id)


def list_all() -> list[Task]:
    """Lista todas las tareas almacenadas.

    Returns:
        Una lista nueva con las tareas en orden de creación; vacía si no hay
        ninguna.
    """
    return list(_tasks.values())


def reset() -> None:
    """Deja el almacén vacío. Se usa entre tests."""
    global _next_id
    _tasks.clear()
    _next_id = 1


reset()
