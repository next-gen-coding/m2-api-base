"""Solución de referencia — Laboratorio Clase 2.

Suite para `users/validation.py`. Cobertura de líneas y ramas al 100%, edge
cases y aserciones específicas (sobreviven pocas mutaciones).

Colocar como `tests/test_validation.py` en la rama `clase2-testing`.
Correr:  pytest --cov=users/validation.py --cov-report=term-missing --cov-branch
"""
import pytest

from users.validation import (
    is_strong_password,
    normalize_email,
    parse_pagination,
    slugify_name,
)


# --------------------------------------------------------------------------- #
# normalize_email
# --------------------------------------------------------------------------- #
def test_normalize_email_recorta_y_pasa_a_minusculas() -> None:
    assert normalize_email("  Ada@Example.COM  ") == "ada@example.com"


def test_normalize_email_ya_normalizado_no_cambia() -> None:
    assert normalize_email("grace@example.com") == "grace@example.com"


def test_normalize_email_vacio_levanta_valueerror() -> None:
    with pytest.raises(ValueError, match="vacío"):
        normalize_email("   ")


@pytest.mark.parametrize(
    "raw",
    [
        "sin-arroba.com",       # falta '@'
        "@example.com",         # sin parte local
        "ada@",                 # sin dominio
        "ada@localhost",        # dominio sin punto
    ],
)
def test_normalize_email_formato_invalido_levanta_valueerror(raw: str) -> None:
    with pytest.raises(ValueError, match="inválido"):
        normalize_email(raw)


# --------------------------------------------------------------------------- #
# is_strong_password
# --------------------------------------------------------------------------- #
def test_password_valida_devuelve_true() -> None:
    assert is_strong_password("Abcd1234") is True


def test_password_de_exactamente_8_es_valida() -> None:
    # Límite inferior: 8 debe pasar (mata la mutación < -> <=).
    assert is_strong_password("Abcd123z") is True


def test_password_de_7_caracteres_es_debil() -> None:
    # Límite: 7 no debe pasar (mata la mutación < -> <=).
    assert is_strong_password("Abc123d") is False


def test_password_sin_mayuscula_es_debil() -> None:
    assert is_strong_password("abcd1234") is False


def test_password_sin_minuscula_es_debil() -> None:
    assert is_strong_password("ABCD1234") is False


def test_password_sin_digito_es_debil() -> None:
    assert is_strong_password("Abcdefgh") is False


def test_password_vacia_es_debil() -> None:
    assert is_strong_password("") is False


# --------------------------------------------------------------------------- #
# parse_pagination
# --------------------------------------------------------------------------- #
def test_parse_pagination_sin_params_usa_defaults() -> None:
    assert parse_pagination({}) == (1, 20)


def test_parse_pagination_valores_normales() -> None:
    assert parse_pagination({"page": "3", "size": "50"}) == (3, 50)


def test_parse_pagination_page_menor_que_1_se_eleva_a_1() -> None:
    assert parse_pagination({"page": "0"}) == (1, 20)


def test_parse_pagination_size_0_se_recorta_a_1() -> None:
    page, size = parse_pagination({"size": "0"})
    assert size == 1


def test_parse_pagination_size_grande_se_recorta_a_max() -> None:
    page, size = parse_pagination({"size": "999"})
    assert size == 100


def test_parse_pagination_respeta_max_size_custom() -> None:
    page, size = parse_pagination({"size": "999"}, max_size=10)
    assert size == 10


def test_parse_pagination_valor_no_numerico_levanta_valueerror() -> None:
    with pytest.raises(ValueError, match="enteros"):
        parse_pagination({"page": "abc"})


# --------------------------------------------------------------------------- #
# slugify_name
# --------------------------------------------------------------------------- #
def test_slugify_name_basico() -> None:
    assert slugify_name("Ada Lovelace") == "ada-lovelace"


def test_slugify_name_quita_acentos_y_enie() -> None:
    assert slugify_name("Núñez Muñoz") == "nunez-munoz"


def test_slugify_name_colapsa_espacios_multiples() -> None:
    assert slugify_name("  Grace   Hopper  ") == "grace-hopper"


def test_slugify_name_cadena_vacia_devuelve_vacio() -> None:
    assert slugify_name("   ") == ""
