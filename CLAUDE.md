# API de usuarios — guía del proyecto

API REST de ejemplo (FastAPI + Pydantic v2). Almacén en memoria, sin base de datos:
el proyecto corre sin infraestructura.

## Estructura

- `main.py` — crea la app y monta los routers.
- `users/` — recurso de ejemplo. Cada recurso sigue el mismo patrón:
  - `routes.py` — rutas HTTP. Sin lógica de negocio: delega en `service.py`.
  - `service.py` — lógica de negocio. Única capa que habla con `repository.py`.
  - `schemas.py` — modelos Pydantic de entrada (`*Create`) y salida.
  - `repository.py` — acceso a datos (aquí, un `dict` en memoria).
- `core/errors.py` — catálogo de errores. Toda respuesta de error sale de aquí.
- `tests/` — un archivo por recurso: `test_<recurso>.py`.

## Convenciones

- Las rutas declaran `response_model=` y devuelven modelos Pydantic, nunca `dict` crudos.
- Los errores se levantan con las funciones de `core/errors.py`
  (`not_found`, `invalid_request`, `already_exists`), no con `HTTPException` a mano.
- La ruta delega en `service.py`; la lógica y las decisiones de error viven ahí.
- Identificadores en inglés y `snake_case`, sin abreviaturas. Mensajes de error en español.
- Cada endpoint nuevo lleva su test en el archivo del recurso, con al menos un caso
  feliz y un caso de error.
- Rutas específicas antes que rutas con parámetro: `/users/search` debe declararse
  **antes** de `/users/{user_id}`.

## Cómo ejecutar

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

uvicorn main:app --reload          # API en http://127.0.0.1:8000  ·  /docs para el Swagger
pytest                             # tests
pytest --cov=. --cov-report=term-missing   # cobertura
ruff check .                       # linter
```

## Fuera de límites

- `migrations/` y `legacy/` — no modificar.

## Recurso tasks (reto M2)

- Endpoints: `POST /tasks` (crear) y `GET /tasks/{task_id}` (consultar).
- Mismo patrón que `users/`: `tasks/routes.py`, `tasks/service.py`,
  `tasks/schemas.py`, `tasks/repository.py`. Montar el router en `main.py`.
- Schemas: `TaskCreate` (title, priority, due_date) y `TaskOut`
  (id, title, priority, due_date, status).
- Validaciones de formato (largo del título, rango de prioridad) en `schemas.py` con Pydantic.
- Reglas de negocio en `service.py`:
  - fecha pasada → `invalid_request`
  - tarea inexistente → `not_found`
  - idempotencia con el header `Idempotency-Key`: misma clave → misma tarea, sin duplicar.
- La fecha de "hoy" se recibe como dependencia en el service para simularla en tests;
  no usar `date.today()` directo dentro de la lógica.
- Repositorio: `dict` en memoria con `reset()` para los tests.
- Docstrings estilo Google (Args, Returns, Raises, ejemplo) en las funciones públicas de `tasks/`.

## Tests del recurso tasks
- Nombres en español, un test por caso, aserciones específicas (valor exacto, no solo "no falla").
- Cobertura: `pytest --cov=tasks --cov-branch --cov-report=term-missing` (meta >90%).