# m2-api-base

API REST de usuarios usada como base en el **Módulo 2 · Clase 1 — Generación de código con IA**.

Es un proyecto pequeño pero completo: tiene convenciones, capas separadas, catálogo
de errores y una suite de tests que pasa. Le falta **una** feature — la que vas a
construir en el laboratorio.

## Requisitos

- Python 3.10 o superior
- (Recomendado) Claude Code instalado

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Uso

```bash
uvicorn main:app --reload          # http://127.0.0.1:8000  ·  Swagger en /docs
```

Endpoints actuales:

| Método | Ruta              | Descripción                                  |
|--------|--------------------|----------------------------------------------|
| GET    | `/health`          | Estado del servicio                          |
| GET    | `/users`           | Lista de usuarios                            |
| GET    | `/users/{id}`      | Un usuario por id (404 si no existe)         |
| POST   | `/users`           | Crea un usuario (409 si el email ya existe)  |
| POST   | `/tasks`           | Crea una tarea asignada a un usuario (201)   |
| GET    | `/tasks`           | Lista todas las tareas (200)                 |
| GET    | `/tasks/{task_id}` | Detalle de una tarea (404 si no existe)      |
| PATCH  | `/tasks/{task_id}` | Actualiza status y/o user_id (200)           |
| DELETE | `/tasks/{task_id}` | Elimina una tarea (204 / 404)                |

## Recurso Tasks

Permite registrar tareas operativas asignadas a un usuario existente (user story USR-143).

Campos: `title` (1-120 chars), `description` (opcional, max 500), `priority` (1-5),
`user_id`, `due_date` (posterior a hoy). El `status` inicia en `todo` y se cambia vía PATCH
(`todo`, `in_progress`, `done`).

**Crear tarea:**

```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Revisar reporte mensual",
    "description": "Validar cifras del Q3",
    "priority": 2,
    "user_id": 1,
    "due_date": "2026-11-01"
  }'
```

**Actualizar status y/o reasignar:**

```bash
curl -X PATCH http://127.0.0.1:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress", "user_id": 2}'
```

## Tests y calidad

```bash
pytest                                                     # correr la suite
pytest --cov=. --cov-branch --cov-report=term-missing      # cobertura de líneas + branch (meta >80%)
ruff check .                                               # linter
```

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

Lee `CLAUDE.md` antes de empezar: ahí están las convenciones que tu código debe respetar.
