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
    return service.list_users()


@router.get("/search", response_model=User)
def search_user_by_email(email: EmailStr = Query(...)) -> User:
    return service.search_by_email(str(email))


@router.get("/{user_id}", response_model=User)
def get_user(user_id: int) -> User:
    return service.get_user(user_id)


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate) -> User:
    return service.create_user(data)
