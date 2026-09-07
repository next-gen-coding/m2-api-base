"""Schemas Pydantic del recurso `users`.

Las rutas devuelven siempre estos modelos (vía `response_model=`), nunca `dict`
crudos. Los modelos de entrada terminan en `Create` / `Update`.
"""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr


class UserCreate(UserBase):
    """Cuerpo de entrada para crear un usuario."""


class User(UserBase):
    """Usuario tal como lo devuelve la API."""

    id: int
    created_at: datetime
