"""Schemas Pydantic del recurso `tasks`.

Las rutas devuelven siempre estos modelos (vía `response_model=`), nunca `dict`
crudos. Las validaciones de formato (largo del título, rango de prioridad) viven
aquí; las reglas de negocio (fecha pasada, idempotencia) viven en `service.py`.
"""
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

TaskStatus = Literal["pending"]


class TaskCreate(BaseModel):
    """Cuerpo de entrada para crear una tarea.

    Attributes:
        title: Nombre de la tarea, de 3 a 100 caracteres.
        priority: Urgencia, entero del 1 (baja) al 5 (alta).
        due_date: Fecha límite en formato `AAAA-MM-DD`.
    """

    title: str = Field(min_length=3, max_length=100)
    priority: int = Field(ge=1, le=5)
    due_date: date

    # TODO: rechazar títulos de solo espacios (validador de campo sobre `title`).


class TaskOut(BaseModel):
    """Tarea tal como la devuelve la API.

    Attributes:
        id: Identificador asignado por el repositorio.
        title: Nombre de la tarea.
        priority: Urgencia, del 1 al 5.
        due_date: Fecha límite.
        status: Estado de la tarea; al crearla siempre es `"pending"`.
    """

    id: int
    title: str
    priority: int
    due_date: date
    status: TaskStatus
