"""Schemas Pydantic del recurso `tasks`.

Las rutas devuelven siempre estos modelos (vía `response_model=`), nunca `dict`
crudos. Las validaciones de formato (largo del título, rango de prioridad) viven
aquí; las reglas de negocio (fecha pasada, idempotencia) viven en `service.py`.
"""
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator

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

    @field_validator("title")
    @classmethod
    def reject_blank_title(cls, title: str) -> str:
        """Rechaza títulos formados solo por espacios.

        Args:
            title: Título recibido, ya validado en largo.

        Returns:
            El título sin modificar.

        Raises:
            ValueError: Si el título queda vacío al quitarle los espacios.

        Example:
            >>> TaskCreate(title="   ", priority=1, due_date=date(2026, 11, 15))
            Traceback (most recent call last):
            ...
            pydantic_core._pydantic_core.ValidationError: ...
        """
        if not title.strip():
            raise ValueError("el título no puede estar formado solo por espacios")
        return title

    @field_validator("priority", mode="before")
    @classmethod
    def reject_boolean_priority(cls, priority: object) -> object:
        """Rechaza `true`/`false` como prioridad; el texto numérico ("3") sigue valiendo.

        Args:
            priority: Valor crudo recibido, antes de convertirlo a entero.

        Returns:
            El valor sin modificar, para que Pydantic lo convierta y valide el rango.

        Raises:
            ValueError: Si el valor es un booleano.

        Example:
            >>> TaskCreate(title="Revisar", priority=True, due_date=date(2026, 11, 15))
            Traceback (most recent call last):
            ...
            pydantic_core._pydantic_core.ValidationError: ...
        """
        if isinstance(priority, bool):
            raise ValueError("la prioridad debe ser un número entero, no un booleano")
        return priority


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
