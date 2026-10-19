"""Tests del recurso `users`.

Estilo de referencia para nuevos tests:
  - un test por caso, con nombre descriptivo en español
  - arrange / act / assert separados por una línea en blanco
  - se comprueba el status code y lo mínimo del cuerpo que da confianza
"""
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from users import service


def test_list_users_devuelve_los_seed(client: TestClient) -> None:
    response = client.get("/users")

    assert response.status_code == 200
    assert len(response.json()) == 4


def test_get_user_existente_devuelve_200(client: TestClient) -> None:
    response = client.get("/users/1")

    assert response.status_code == 200
    assert response.json()["email"] == "ada@example.com"


def test_get_user_inexistente_devuelve_404(client: TestClient) -> None:
    response = client.get("/users/999")

    assert response.status_code == 404
    assert "no encontrado" in response.json()["detail"]


def test_create_user_devuelve_201_y_el_usuario(client: TestClient) -> None:
    payload = {"name": "Margaret Hamilton", "email": "margaret@example.com"}

    response = client.post("/users", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 5
    assert body["name"] == "Margaret Hamilton"


def test_create_user_email_duplicado_devuelve_409(client: TestClient) -> None:
    payload = {"name": "Otra Ada", "email": "ada@example.com"}

    response = client.post("/users", json=payload)

    assert response.status_code == 409


def test_create_user_email_invalido_devuelve_422(client: TestClient) -> None:
    payload = {"name": "Sin Email", "email": "no-es-un-email"}

    response = client.post("/users", json=payload)

    assert response.status_code == 422


# GET /users/search — ver docs/reto-m2-especificacion.md.
# Los 422 comprueban `loc`: hoy `/users/{user_id}` captura `/users/search` y ya
# responde 422 (int_parsing sobre `user_id`), así que el status solo no basta (CA5).


def test_search_user_email_existente_devuelve_200(client: TestClient) -> None:
    response = client.get("/users/search", params={"email": "ada@example.com"})

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 1
    assert body["name"] == "Ada Lovelace"
    assert body["email"] == "ada@example.com"
    assert "created_at" in body


@pytest.mark.parametrize("email", ["ADA@EXAMPLE.COM", "Ada@Example.Com"])
def test_search_user_ignora_mayusculas_devuelve_200(client: TestClient, email: str) -> None:
    response = client.get("/users/search", params={"email": email})

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_search_user_encuentra_email_guardado_con_mayusculas(client: TestClient) -> None:
    payload = {"name": "Margaret Hamilton", "email": "Margaret.Hamilton@Example.com"}
    created = client.post("/users", json=payload).json()

    response = client.get("/users/search", params={"email": "margaret.hamilton@example.com"})

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_search_user_con_espacios_en_los_extremos_devuelve_200(client: TestClient) -> None:
    response = client.get("/users/search", params={"email": "  alan@example.com  "})

    assert response.status_code == 200
    assert response.json()["id"] == 2


def test_search_user_email_inexistente_devuelve_404(client: TestClient) -> None:
    response = client.get("/users/search", params={"email": "nadie@example.com"})

    assert response.status_code == 404
    assert "no encontrado" in response.json()["detail"]
    assert "nadie@example.com" in response.json()["detail"]


@pytest.mark.parametrize("email", ["da@example.com", "ada@example.co", "ada+otro@example.com"])
def test_search_user_no_hace_coincidencias_parciales_devuelve_404(
    client: TestClient, email: str
) -> None:
    response = client.get("/users/search", params={"email": email})

    assert response.status_code == 404


@pytest.mark.parametrize("email", ["no-es-email", "", "ada@example"])
def test_search_user_email_invalido_devuelve_422(client: TestClient, email: str) -> None:
    response = client.get("/users/search", params={"email": email})

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "email"]


def test_search_user_mas_sin_codificar_devuelve_422(client: TestClient) -> None:
    # En una query string, un "+" literal se decodifica como espacio: el cliente
    # debe enviarlo como %2B (riesgo 4 de la especificación).
    response = client.get("/users/search?email=a+b@example.com")

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "email"]


def test_search_user_sin_parametro_devuelve_422(client: TestClient) -> None:
    response = client.get("/users/search")

    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["loc"] == ["query", "email"]
    assert error["type"] == "missing"


def test_search_user_encuentra_usuario_recien_creado(client: TestClient) -> None:
    payload = {"name": "Margaret Hamilton", "email": "margaret+nasa@example.com"}
    created = client.post("/users", json=payload).json()

    response = client.get("/users/search", params={"email": "margaret+nasa@example.com"})

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_user_by_email_devuelve_el_usuario() -> None:
    user = service.get_user_by_email("grace@example.com")

    assert user.id == 3
    assert user.name == "Grace Hopper"


def test_get_user_by_email_inexistente_lanza_404() -> None:
    with pytest.raises(HTTPException) as error:
        service.get_user_by_email("nadie@example.com")

    assert error.value.status_code == 404
    assert "no encontrado" in error.value.detail
