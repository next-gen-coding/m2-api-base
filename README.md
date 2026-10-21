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
| POST   | `/tasks`          | Crea una tarea (422 si el cuerpo es inválido o la fecha límite es pasada) |

## Módulo `tasks`

`POST /tasks` crea una tarea y devuelve **201** con la tarea creada (incluye `id` y
`created_at`). Los datos se guardan en memoria: se pierden al reiniciar el servidor.

Campos del cuerpo JSON:

| Campo         | Tipo     | Obligatorio | Regla                                               |
|---------------|----------|-------------|-----------------------------------------------------|
| `title`       | string   | sí          | De 1 a 120 caracteres                               |
| `description` | string   | no          | Hasta 500 caracteres                                |
| `priority`    | string   | no          | `low`, `medium` o `high` (por defecto `medium`)     |
| `due_date`    | `YYYY-MM-DD` | no      | No puede ser anterior a hoy (fecha UTC); hoy es válido |

Ejemplo de payload válido:

```json
{
  "title": "Write report",
  "description": "Quarterly summary",
  "priority": "high",
  "due_date": "2030-12-31"
}
```

Errores: **422** si falta `title` o está vacío, si `priority` no es uno de los valores
permitidos, o si `due_date` es una fecha pasada.

### Probarlo paso a paso

1. Instala las dependencias (sección [Instalación](#instalación)).
2. Arranca el servidor:

   ```bash
   uvicorn main:app --reload
   ```

3. Abre el Swagger UI en <http://127.0.0.1:8000/docs>.
4. Despliega `POST /tasks`, pulsa **Try it out**, pega el payload de arriba y pulsa **Execute**.

También desde la terminal:

```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Write report", "priority": "high", "due_date": "2030-12-31"}'
```

### Tests del módulo

```bash
pytest tests/test_tasks.py                          # solo los tests de tasks
pytest                                              # toda la suite
pytest --cov=tasks --cov-report=term-missing        # cobertura de tasks
```

## Tests y calidad

```bash
pytest                                       # correr la suite
pytest --cov=. --cov-report=term-missing     # con cobertura
ruff check .                                 # linter
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
