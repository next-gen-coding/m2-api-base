"""Lógica de negocio del recurso `users`.

Las rutas no acceden al repositorio directamente: pasan por aquí. Esta capa es la
única que conoce `repository.py` y la que decide cuándo algo es un error de
dominio (usando `core.errors`).
"""
from core import errors
from users import repository
from users.schemas import User, UserCreate


def get_user(user_id: int) -> User:
    """Devuelve el usuario con ese id. Lanza 404 (`errors.not_found`) si no existe."""
    user = repository.get(user_id)
    if user is None:
        raise errors.not_found("usuario", user_id)
    return user


def get_user_by_email(email: str) -> User:
    """Devuelve el usuario cuyo email coincide exactamente, sin distinguir mayúsculas.

    Es el mismo criterio que usa `create_user` para detectar duplicados. No hace
    coincidencias parciales. Lanza 404 (`errors.not_found`) si nadie tiene ese email.
    """
    user = repository.find_by_email(email)
    if user is None:
        raise errors.not_found("usuario", email)
    return user


def list_users() -> list[User]:
    """Devuelve todos los usuarios, en orden de creación."""
    return repository.list_all()


def create_user(data: UserCreate) -> User:
    """Crea un usuario. Lanza 409 (`errors.already_exists`) si el email ya está registrado.

    La unicidad del email no distingue mayúsculas (ver `repository.find_by_email`).
    """
    if repository.find_by_email(str(data.email)) is not None:
        raise errors.already_exists("usuario", data.email)
    return repository.add(name=data.name, email=str(data.email))
