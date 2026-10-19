"""Rutas HTTP del recurso `users`.

Patrón de referencia para nuevas rutas:
  - un `APIRouter` con `prefix` y `tags`
  - `response_model=` siempre; nunca devolver `dict` crudos
  - la función delega en `service.py` y no contiene lógica de negocio
  - los errores los levanta `service.py` con `core.errors`
"""
from fastapi import APIRouter, Query, status
from pydantic import EmailStr

from users import service
from users.schemas import User, UserCreate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[User])
def list_users() -> list[User]:
    """Lista todos los usuarios."""
    return service.list_users()


# Debe declararse antes de `/{user_id}`: si no, "search" se interpreta como id (422).
@router.get("/search", response_model=User)
def search_user(email: EmailStr = Query()) -> User:
    """Busca un usuario por email. 422 si el formato no es válido, 404 si no existe."""
    return service.get_user_by_email(email)


@router.get("/{user_id}", response_model=User)
def get_user(user_id: int) -> User:
    """Devuelve un usuario por id. 404 si no existe, 422 si el id no es un entero."""
    return service.get_user(user_id)


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate) -> User:
    """Crea un usuario. 201 si se crea, 409 si el email ya existe, 422 si hay datos inválidos."""
    return service.create_user(data)
