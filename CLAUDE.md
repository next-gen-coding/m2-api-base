# API de usuarios y tareas — guía del proyecto

API REST de ejemplo (FastAPI + Pydantic v2). Almacén en memoria, sin base de datos:
el proyecto corre sin infraestructura.

## Estructura

- `main.py` — crea la app y monta los routers.
- `users/` — recurso de usuarios. Cada recurso sigue el mismo patrón:
  - `routes.py` — rutas HTTP. Sin lógica de negocio: delega en `service.py`.
  - `service.py` — lógica de negocio. Única capa que habla con `repository.py`.
  - `schemas.py` — modelos Pydantic de entrada (`*Create`, `*Update`) y salida.
  - `repository.py` — acceso a datos (aquí, un `dict` en memoria).
- `tasks/` — recurso de tareas operativas asignadas a un usuario. Mismo patrón que `users/`.
  Spec y criterios de aceptación: `docs/spec-tareas.md`.
- `docs/` — specs de las features y evidencias del proceso.
- `core/errors.py` — catálogo de errores. Toda respuesta de error sale de aquí.
- `tests/` — un archivo por recurso: `test_<recurso>.py`.

## Recurso `tasks` — reglas de dominio

- **Endpoints**: POST (201), GET lista (200), GET detalle (200), DELETE (204), PATCH (200).
- **status**: valores permitidos `todo`, `in_progress`, `done`. Siempre inicia en `todo`;
  no se acepta en el POST, solo se cambia vía PATCH. Transiciones libres entre estados.
- **priority**: entero de 1 (más alta) a 5. Fuera de rango → 422.
- **title**: de 1 a 120 caracteres.
- **description**: opcional (puede ser null), máximo 500 caracteres.
- **due_date**: tipo `date` (sin hora), debe ser posterior a hoy (hoy = 422).
- **created_at**: tipo `datetime` en UTC, por consistencia con el recurso `users`.
- **PATCH** solo modifica `user_id` y/o `status`; usa el schema `TaskUpdate` con campos
  opcionales. Las mismas validaciones del POST aplican en el PATCH.
- **Response** del POST, GET y PATCH devuelve todos los campos: id, title, description,
  priority, status, user_id, due_date, created_at.
- **Validación de usuario**: `tasks/service.py` valida el usuario llamando a
  `users.service`, **nunca** a `users/repository.py` directamente. Si el usuario no
  existe → 404, tanto en POST como en PATCH.
- **Operaciones sobre tareas inexistentes**: GET, DELETE y PATCH sobre un task_id
  inexistente regresan 404.
- **Idempotencia**: PATCH repetido con el mismo cuerpo devuelve 200 con la misma tarea.
  DELETE responde 204 la primera vez y 404 después.

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
pytest --cov=. --cov-branch --cov-report=term-missing   # cobertura líneas + branch (meta >80%)
# mutation testing: manual — mutar una línea de tasks/, correr pytest, revertir con git checkout tasks/
ruff check .                       # linter
```

## Fuera de límites

- `migrations/` y `legacy/` — no modificar.
