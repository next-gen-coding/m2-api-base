# m2-api-base

API REST de usuarios usada como base en el **Módulo 2 · Clase 1 — Generación de código con IA**.

Es un proyecto pequeño pero completo: tiene convenciones, capas separadas, catálogo
de errores y una suite de tests que pasa. Le falta **una** feature — la que vas a
construir en el laboratorio.

> En la rama `feature/reto-m2-ia` esa feature (`GET /users/search`) ya está implementada.
> Cambios en [`CHANGELOG.md`](CHANGELOG.md); especificación y evidencias en
> [`docs/`](docs/reto-m2-evidencias.md).

## Requisitos

- Python 3.10 o superior (verificado con 3.12.3)
- Dependencias en `requirements.txt` (FastAPI, Pydantic v2, email-validator, uvicorn,
  pytest, pytest-cov, ruff)
- (Recomendado) Claude Code instalado

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate  ·  PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Ejecuta siempre con el intérprete del `.venv`: fuera de él pueden faltar `pytest` o
`email-validator` (`No module named pytest`).

## Uso

```bash
uvicorn main:app --reload          # http://127.0.0.1:8000  ·  Swagger en /docs
```

Endpoints actuales:

| Método | Ruta              | Descripción                     |
|--------|-------------------|---------------------------------|
| GET    | `/health`         | Estado del servicio             |
| GET    | `/users`          | Lista de usuarios               |
| GET    | `/users/search?email=` | Un usuario por email, sin distinguir mayúsculas (404 si no existe, 422 si el formato es inválido) |
| GET    | `/users/{id}`     | Un usuario por id (404 si no existe) |
| POST   | `/users`          | Crea un usuario (409 si el email ya existe) |

### Búsqueda por email: `GET /users/search?email=<email>`

- `email` (query, obligatorio): se valida con `EmailStr` y se le quitan los espacios de los extremos.
- La coincidencia es **exacta** y **no distingue mayúsculas**, con el mismo criterio que el
  409 de `POST /users`. No hay coincidencias parciales.
- Respuesta `200`: un único objeto `User`, no una lista.
- Un `+` en el email debe enviarse codificado como `%2B`; sin codificar llega como espacio
  y la respuesta es `422`.

Ejemplos reales (servidor levantado con `uvicorn`, datos semilla; `created_at` varía):

```http
GET /users/search?email=ada@example.com
→ 200 OK
{"name": "Ada Lovelace", "email": "ada@example.com", "id": 1, "created_at": "2026-10-19T16:56:19.487424Z"}

GET /users/search?email=ADA@EXAMPLE.COM
→ 200 OK   (mismo usuario, id 1)

GET /users/search?email=nadie@example.com
→ 404 Not Found
{"detail": "usuario no encontrado: nadie@example.com"}

GET /users/search?email=no-es-email
→ 422 Unprocessable Entity
{"detail": [{"type": "value_error", "loc": ["query", "email"],
  "msg": "value is not a valid email address: An email address must have an @-sign.", ...}]}

GET /users/search
→ 422 Unprocessable Entity
{"detail": [{"type": "missing", "loc": ["query", "email"], "msg": "Field required", "input": null}]}

GET /users/search?email=margaret%2Bnasa@example.com      (tras crearlo con POST /users)
→ 200 OK
{"name": "Margaret Hamilton", "email": "margaret+nasa@example.com", "id": 5, ...}
```

Los `422` de formato los genera Pydantic, con mensajes en inglés. El `404` sale del
catálogo `core/errors.py`, en español.

## Tests y calidad

```bash
pytest                                       # correr la suite
pytest --cov=. --cov-report=term-missing     # con cobertura (incluye tests/ en la medición)
pytest --cov=users --cov=core --cov=main --cov-branch --cov-report=term-missing   # solo código, con ramas
ruff check .                                 # linter
```

Último resultado medido en `feature/reto-m2-ia`: 23 tests en verde, líneas 80/82 (97,56 %),
ramas 8/8 (100 %), `ruff check .` sin errores. Detalle en `docs/reto-m2-evidencias.md`.

## Ramas del módulo

`main` es la base de la **Clase 1**. Cada clase tiene su rama de trabajo y su
rama de solución:

| Clase | Rama de trabajo | Solución | Qué añade |
|-------|-----------------|----------|-----------|
| 1 · Generación | `main` | `solucion-clase1` | La base. Falta `GET /users/search`. |
| 2 · Testing | `clase2-testing` | `solucion-clase2` | `users/validation.py` sin tests → llévalo a >80%. |
| 3 · Debugging | `clase3-debugging` | `solucion-clase3` | Recurso `reports/` con 3 bugs plantados. |
| 4 · Review | `clase4-review` | `solucion-clase4` | PR de `GET /reports/export` con issues (verde). |

```bash
git switch clase2-testing     # o la que toque
```

## Tarea del laboratorio (Clase 1)

Añadir `GET /users/search?email=<email>`:

- **200** con el usuario si existe
- **422** si el formato del email es inválido
- **404** si no hay ningún usuario con ese email
- con su test en `tests/test_users.py`, siguiendo el estilo del archivo

**Estado en `feature/reto-m2-ia`:** implementada y cubierta por 17 tests nuevos
(15 de integración y 2 unitarios del servicio).

Lee `CLAUDE.md` antes de empezar: ahí están las convenciones que tu código debe respetar.
