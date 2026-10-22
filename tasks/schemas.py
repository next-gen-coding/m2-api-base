"""Schemas Pydantic del recurso `tasks`.

Las rutas devuelven siempre estos modelos (vía `response_model=`), nunca `dict`
crudos. Los modelos de entrada terminan en `Create` / `Update`.
"""
from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=120)

    @field_validator("title")
    @classmethod
    def title_no_solo_espacios(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El título no puede contener solo espacios")
        return v
    description: str | None = Field(default=None, max_length=500)
    priority: int = Field(ge=1, le=5)
    user_id: int
    due_date: date


class TaskCreate(TaskBase):
    """Cuerpo de entrada para crear una tarea."""


class TaskUpdate(BaseModel):
    """Cuerpo de entrada para actualizar una tarea (PATCH)."""

    status: str | None = None
    user_id: int | None = None


class Task(TaskBase):
    """Tarea tal como la devuelve la API."""

    id: int
    status: str
    created_at: datetime
