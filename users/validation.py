"""Utilidades de validación del recurso `users`.

Funciones puras: sin FastAPI, sin estado, sin I/O. Fáciles de probar de forma
aislada.

Este módulo NO tiene tests todavía — llevarlo a >80% de cobertura es el
objetivo del laboratorio de la Clase 2.
"""
from __future__ import annotations

MIN_PASSWORD_LEN = 8
DEFAULT_PAGE_SIZE = 20


def normalize_email(raw: str) -> str:
    """Normaliza un email: recorta espacios y pasa a minúsculas.

    Levanta ValueError si queda vacío o si no tiene una '@' con texto a ambos
    lados y un punto en el dominio.
    """
    email = raw.strip().lower()
    if not email:
        raise ValueError("el email no puede estar vacío")
    local, sep, domain = email.partition("@")
    if not sep or not local or not domain or "." not in domain:
        raise ValueError(f"email inválido: {raw!r}")
    return email


def is_strong_password(password: str) -> bool:
    """True si la contraseña tiene 8+ caracteres y mezcla mayúscula, minúscula y dígito."""
    if len(password) < MIN_PASSWORD_LEN:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_upper and has_lower and has_digit


def parse_pagination(params: dict[str, str], *, max_size: int = 100) -> tuple[int, int]:
    """Devuelve (page, size) a partir de los query params.

    - `page`: por defecto 1; valores menores que 1 se elevan a 1.
    - `size`: por defecto 20; se recorta al rango [1, max_size].
    - Valores no numéricos levantan ValueError.
    """
    try:
        page = int(params.get("page", 1))
        size = int(params.get("size", DEFAULT_PAGE_SIZE))
    except (TypeError, ValueError):
        raise ValueError("page y size deben ser enteros") from None
    page = max(page, 1)
    size = min(max(size, 1), max_size)
    return page, size


def slugify_name(name: str) -> str:
    """Convierte un nombre en un slug: minúsculas, sin acentos comunes, espacios a '-'.

    Cadenas vacías o de solo espacios devuelven "".
    """
    table = str.maketrans("áéíóúüñ", "aeiouun")
    slug = name.strip().lower().translate(table)
    return "-".join(part for part in slug.split() if part)
