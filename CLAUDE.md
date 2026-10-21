# API de gestión — guía del proyecto

API REST de ejemplo (FastAPI + Pydantic v2). Almacén en memoria, sin base de datos:
el proyecto corre sin infraestructura.

## Estructura

- `main.py` — crea la app y monta los routers de cada módulo.
- `<recurso>/` (ej. `users/`, `tasks/`) — cada recurso sigue estrictamente el mismo patrón:
  - `routes.py` — rutas HTTP. Sin lógica de negocio: delega en `service.py`.
  - `service.py` — lógica de negocio. Única capa que habla con `repository.py`.
  - `schemas.py` — modelos Pydantic de entrada (`*Create`, `*Update`) y salida.
  - `repository.py` — acceso a datos (almacenamiento en un `dict` en memoria).
- `core/errors.py` — catálogo de errores. Toda respuesta de error sale de aquí.
- `tests/` — un archivo por recurso: `test_users.py`, `test_tasks.py`, etc.

## Convenciones

- Las rutas declaran `response_model=` y devuelven modelos Pydantic, nunca `dict` crudos.
- Los errores se levantan con las funciones de `core/errors.py`
  (`not_found`, `invalid_request`, `already_exists`), no con `HTTPException` a mano.
- La ruta delega en `service.py`; la lógica y las decisiones de error viven ahí.
- Identificadores en inglés y `snake_case`, sin abreviaturas. Mensajes de error en español.
- Cada endpoint nuevo lleva su test en el archivo del recurso correspondiente, con al menos un caso feliz y los casos de error (edge cases).
- Rutas específicas antes que rutas con parámetro: las rutas estáticas o de búsqueda (ej. `/tasks/search`) deben declararse **antes** de las rutas con variables en path (ej. `/tasks/{task_id}`).

## Cómo ejecutar

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

uvicorn main:app --reload          # API en [http://127.0.0.1:8000](http://127.0.0.1:8000)  ·  /docs para el Swagger
pytest                             # tests
pytest --cov=. --cov-report=term-missing   # cobertura
ruff check .                       # linter