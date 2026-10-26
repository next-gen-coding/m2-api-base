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

| Método | Ruta              | Descripción                     |
|--------|-------------------|---------------------------------|
| GET    | `/health`         | Estado del servicio             |
| GET    | `/users`          | Lista de usuarios               |
| GET    | `/users/{id}`     | Un usuario por id (404 si no existe) |
| POST   | `/users`          | Crea un usuario (409 si el email ya existe) |

## Tests y calidad

```bash
pytest                                       # correr la suite
pytest --cov=. --cov-report=term-missing     # con cobertura
ruff check .                                 # linter
```

## Recurso tasks

Permite al equipo registrar y consultar sus tareas operativas, para que no se pierda
trabajo sin registrar. Solo se pueden **crear** y **consultar** tareas; editar, borrar,
listar y asignar usuarios quedan fuera de alcance. La especificación completa está en
[`docs/spec-tasks.md`](docs/spec-tasks.md).

El código sigue el mismo patrón que `users/`:

- `tasks/routes.py` — rutas HTTP; solo delegan en el service.
- `tasks/service.py` — reglas de negocio: fecha pasada, tarea inexistente, idempotencia.
- `tasks/schemas.py` — `TaskCreate` (entrada) y `TaskOut` (salida), con las validaciones de formato.
- `tasks/repository.py` — almacén en memoria (`dict`), con `reset()` para los tests.

La fecha de "hoy" llega al service como dependencia (`get_today` en `routes.py`), así
los tests la fijan sin depender del reloj.

### Endpoints

| Método | Ruta               | Descripción                                        |
|--------|--------------------|----------------------------------------------------|
| POST   | `/tasks`           | Crea una tarea (201). Header opcional `Idempotency-Key` |
| GET    | `/tasks/{task_id}` | Consulta una tarea (200, o 404 si no existe)       |

### Campos y reglas

| Campo      | Tipo                 | Regla                                                                 | Si no se cumple |
|------------|----------------------|-----------------------------------------------------------------------|-----------------|
| `title`    | texto                | Obligatorio; no solo espacios; mínimo 3 caracteres sin contar los espacios de los extremos; máximo 100 contándolos | 422 |
| `priority` | entero               | Del 1 (baja) al 5 (alta); no se aceptan decimales ni booleanos        | 422 |
| `due_date` | fecha `AAAA-MM-DD`   | Hoy o una fecha futura                                                | 422 |

La respuesta (`TaskOut`) incluye además `id` (lo asigna el servidor, empezando en 1) y
`status`, que al crear la tarea siempre vale `"pending"`.

### Ejemplos

**201 — crear una tarea**

```http
POST /tasks
Content-Type: application/json

{"title": "Revisar respaldo nocturno", "priority": 4, "due_date": "2026-11-15"}
```

```json
{"id": 1, "title": "Revisar respaldo nocturno", "priority": 4, "due_date": "2026-11-15", "status": "pending"}
```

**Idempotencia con `Idempotency-Key`** — si se repite el envío con la misma clave, se
devuelve la tarea original (mismo `id`) y no se crea otra:

```http
POST /tasks
Idempotency-Key: abc-123
Content-Type: application/json

{"title": "Revisar respaldo nocturno", "priority": 4, "due_date": "2026-11-15"}
```

La primera y la segunda petición responden **201** con el mismo cuerpo:

```json
{"id": 1, "title": "Revisar respaldo nocturno", "priority": 4, "due_date": "2026-11-15", "status": "pending"}
```

Sin el header, o con claves distintas, cada envío crea una tarea nueva.

**422 — dato con formato inválido** (lo valida Pydantic en `schemas.py`; `detail` es una lista):

```http
POST /tasks

{"title": "  ab ", "priority": 4, "due_date": "2026-11-15"}
```

```json
{"detail": [{"type": "value_error", "loc": ["body", "title"], "msg": "Value error, el título debe tener al menos 3 caracteres sin espacios en los extremos", "input": "  ab ", "ctx": {"error": {}}}]}
```

**422 — fecha límite pasada** (regla de negocio en `service.py`; `detail` es un texto):

```http
POST /tasks

{"title": "Revisar respaldo nocturno", "priority": 4, "due_date": "2026-10-01"}
```

```json
{"detail": "La fecha límite 2026-10-01 ya pasó; debe ser hoy o una fecha futura."}
```

**200 / 404 — consultar una tarea**

```http
GET /tasks/1
```

```json
{"id": 1, "title": "Revisar respaldo nocturno", "priority": 4, "due_date": "2026-11-15", "status": "pending"}
```

```http
GET /tasks/999
```

```json
{"detail": "tarea no encontrado: 999"}
```

### Tests y cobertura

Los tests de tasks están en `tests/test_tasks.py` (por HTTP) y `tests/test_tasks_service.py`
(unitarios del service con el repositorio simulado).

```bash
pytest tests/test_tasks.py tests/test_tasks_service.py -q              # solo tasks
pytest --cov=tasks --cov-branch --cov-report=term-missing              # cobertura de tasks (meta >90%)
ruff check .
```

### Comportamientos conocidos

Lo que sigue es el comportamiento **actual**, cubierto por tests. Si se decide
cambiarlo, hay que actualizar esos tests.

- **La prioridad acepta texto numérico:** `"priority": "3"` se convierte a `3` y la
  tarea se crea con 201. En cambio, `"alta"`, `3.5`, `true` y `false` dan 422.
- **El título se guarda sin recortar:** `"  abc  "` se guarda y se devuelve como
  `"  abc  "`. Los espacios de los extremos solo se ignoran para validar el mínimo de 3
  caracteres; el máximo de 100 sí los cuenta.

Otros detalles que conviene conocer:

- **Hay dos formatos de 422:** los errores de formato (Pydantic) devuelven `detail` como
  lista de objetos, y los de negocio (fecha pasada) como texto.
- **Algunos mensajes de 422 están en inglés:** los que genera Pydantic por su cuenta,
  por ejemplo `"Input should be less than or equal to 5"` para la prioridad 6.
- **El 404 dice "tarea no encontrado"**, con la concordancia mal. `core/errors.py` ya
  admite `gender="feminine"`, pero `tasks/service.py` todavía no lo usa.
- **La idempotencia no compara el cuerpo:** si se reutiliza una clave con datos
  distintos, se devuelve la tarea original sin avisar, y tampoco se revalida la fecha.

## Tarea del laboratorio

Añadir `GET /users/search?email=<email>`:

- **200** con el usuario si existe
- **422** si el formato del email es inválido
- **404** si no hay ningún usuario con ese email
- con su test en `tests/test_users.py`, siguiendo el estilo del archivo

Lee `CLAUDE.md` antes de empezar: ahí están las convenciones que tu código debe respetar.
