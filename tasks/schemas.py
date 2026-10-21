"""Schemas Pydantic del recurso `tasks`.

Las rutas devuelven siempre estos modelos (vía `response_model=`), nunca `dict`
crudos. Los modelos de entrada terminan en `Create` / `Update`.
"""
from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class TaskPriority(str, Enum):
    """Niveles de prioridad permitidos para una tarea."""

    low = "low"
    medium = "medium"
    high = "high"


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    priority: TaskPriority = TaskPriority.medium
    due_date: date | None = None


class TaskCreate(TaskBase):
    """Cuerpo de entrada para crear una tarea."""


class TaskUpdate(BaseModel):
    """Cuerpo de entrada para actualizar una tarea: todos los campos son opcionales."""

    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    priority: TaskPriority | None = None
    due_date: date | None = None


class Task(TaskBase):
    """Tarea tal como la devuelve la API."""

    id: int
    created_at: datetime
