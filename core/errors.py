"""Catálogo de errores de la API.

Todas las rutas deben levantar errores a través de estas funciones, para que los
códigos de estado y el formato de la respuesta sean consistentes en todo el
proyecto. No usar `HTTPException` directamente en las rutas.
"""
from typing import Literal

from fastapi import HTTPException, status

GrammaticalGender = Literal["masculine", "feminine"]

_FOUND_BY_GENDER: dict[GrammaticalGender, str] = {
    "masculine": "encontrado",
    "feminine": "encontrada",
}


def not_found(
    resource: str,
    identifier: object,
    *,
    gender: GrammaticalGender = "masculine",
) -> HTTPException:
    """404 — el recurso pedido no existe.

    `gender` hace concordar el mensaje con el sustantivo del recurso
    ("usuario no encontrado", "tarea no encontrada").
    """
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource} no {_FOUND_BY_GENDER[gender]}: {identifier}",
    )


def invalid_request(message: str) -> HTTPException:
    """422 — la petición llegó bien formada pero no es válida a nivel de dominio."""
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail=message,
    )


def already_exists(resource: str, identifier: object) -> HTTPException:
    """409 — el recurso que se quiere crear ya existe."""
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"{resource} ya existe: {identifier}",
    )
