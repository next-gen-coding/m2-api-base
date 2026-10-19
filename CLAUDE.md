# API de usuarios — guía del proyecto

API REST de ejemplo (FastAPI + Pydantic v2) usada como base del Módulo 2. Almacén en
memoria, sin base de datos: el proyecto corre sin infraestructura. Uso, endpoints
públicos y ramas del curso: ver `README.md`.

## Arquitectura

Capas por recurso, con dependencias en un solo sentido:
`routes.py → service.py → repository.py`, y `core/errors.py` para los errores.

- `main.py` — punto de entrada (`main:app`). Crea la app y monta los routers.
- `users/` — recurso de ejemplo. Cada recurso sigue el mismo patrón:
  - `routes.py` — `APIRouter(prefix=..., tags=...)`. Sin lógica de negocio: delega en `service.py`.
  - `service.py` — lógica de negocio y decisiones de error. Única capa que habla con `repository.py`.
  - `schemas.py` — modelos Pydantic: base (`UserBase`), entrada (`*Create` / `*Update`) y salida (`User`).
  - `repository.py` — acceso a datos: un `dict` global en memoria con 4 usuarios semilla
    (`@example.com`) y `reset()` para restaurarlos.
- `core/errors.py` — catálogo de errores: `not_found` (404), `invalid_request` (422),
  `already_exists` (409). Toda respuesta de error de dominio sale de aquí.
- `tests/` — un archivo por recurso: `test_<recurso>.py`. Fixtures en `tests/conftest.py`.
- `docs/` — especificaciones de trabajo (p. ej. `docs/reto-m2-especificacion.md`).

## Entorno y versiones verificadas

Trabaja **siempre** con el intérprete de `.venv`: el Python global de esta máquina no tiene
`pytest` ni `email-validator`, y `pytest` o cualquier import de `users.schemas` fallan fuera del venv.

- Python: requiere `>=3.10` (`pyproject.toml`); el `.venv` usa 3.12.3.
- Instalado en `.venv`: fastapi 0.143.0 (starlette 1.7.0), pydantic 2.14.0,
  email-validator 2.3.0, httpx 0.28.1, uvicorn 0.54.0, pytest 9.1.1, pytest-cov 7.1.0, ruff 0.17.0.
- `requirements.txt` solo fija mínimos (`>=`), sin lock: no subas ni fijes versiones sin pedirlo.
- Ruff: `line-length = 100`, `target-version = "py310"`, reglas `E, F, I, UP, B`.
  `fastapi.Query/Path/Body/Header/Depends` están permitidos como defaults (B008).

## Convenciones de estilo y tipado

- Identificadores en inglés y `snake_case`, sin abreviaturas. Mensajes de error en español.
- Anota tipos en todas las funciones, incluido el retorno. Sintaxis moderna (la exige `UP`):
  `User | None`, `list[User]`, `dict[int, User]`; nada de `Optional`/`List`.
- Docstring de módulo en cada archivo con código; imports ordenados (regla `I`).
- Tests: nombre descriptivo en español (`test_<accion>_<caso>_devuelve_<status>`),
  arrange / act / assert separados por una línea en blanco, `client: TestClient` y `-> None`.
- `ruff format` **no** se aplica en este repo (reformatearía 8 archivos). No lo ejecutes sobre
  todo el proyecto: genera diffs ajenos a la tarea.

## Reglas para modificar código

**Endpoints**
- Declaran `response_model=` y devuelven modelos Pydantic, nunca `dict` crudos.
  (`GET /health` en `main.py` es una excepción heredada: no la copies.)
- La función de ruta solo delega en `service.py`; no accede a `repository.py`.
- Rutas específicas antes que rutas con parámetro: `/users/search` debe declararse
  **antes** de `/users/{user_id}`; si no, responde 422 `int_parsing` sobre `user_id`.
- Códigos explícitos con `fastapi.status` (p. ej. `status.HTTP_201_CREATED`).

**Errores**
- Se levantan desde `service.py` con `core/errors.py`, nunca con `HTTPException` a mano.
- La validación de formato que hace Pydantic produce su propio 422 (lista `detail` con `loc`,
  mensajes en inglés); el 422 de dominio usa `invalid_request` (texto en español).
  Elige uno de forma deliberada y documéntalo.

**Esquemas**
- Reutiliza `UserBase` y los tipos existentes (`EmailStr`, `Field`) antes de crear otros.
- La unicidad de email es *case-insensitive* (`repository.find_by_email` compara en minúsculas).
  Mantén ese criterio en cualquier búsqueda o validación de email.

**Servicios y repositorio**
- La lógica y las decisiones de error viven en `service.py`.
- `repository.py` expone funciones simples (`add`, `get`, `list_all`, `find_by_email`, `reset`);
  si añades una, mantenla sin lógica de negocio.

**Dependencias**
- No añadas paquetes sin aprobación explícita. Si se aprueban, van a `requirements.txt`.

## Pruebas

- Tests de integración HTTP con `TestClient` sobre la app real. No hay mocks ni
  `dependency_overrides`: el almacén en memoria hace innecesario simularlo.
- Fixtures (`tests/conftest.py`):
  - `_reset_data` (autouse): llama a `repository.reset()` antes y después de cada test.
  - `client`: `TestClient(app)`.
- Los tests unitarios de servicio pueden llamar a `service.*` directamente y comprobar
  errores con `pytest.raises(HTTPException)` y `status_code`.
- Cada endpoint nuevo lleva sus tests en el archivo del recurso, con al menos un caso feliz
  y uno de error. Cubre también casos límite y la regresión de los endpoints existentes.
- Los avisos de deprecación de Starlette/anyio están filtrados en `pyproject.toml`; no
  los silencies en otros sitios.

## Comandos

Verificados con el `.venv`: `pytest`, ambas variantes de cobertura y `ruff check .`.
La instalación y `uvicorn` están documentados pero no se ejecutaron en la verificación.

```powershell
.venv\Scripts\Activate.ps1                    # bash: source .venv/Scripts/activate
pip install -r requirements.txt

pytest                                                          # suite (6 tests en verde)
pytest --cov=users --cov=core --cov=main --cov-report=term-missing   # cobertura sin contar tests/
ruff check .                                                    # linter (limpio)
uvicorn main:app --reload                     # documentado; Swagger en /docs
```

`pytest --cov=. --cov-report=term-missing` también funciona, pero incluye `tests/` en la
medición e infla el porcentaje. Umbral del reto: cobertura ≥ 80 %.

## Seguridad

- No escribas, registres ni subas secretos, tokens ni credenciales. `.env` está en
  `.gitignore`; no lo crees con valores reales ni lo añadas al repositorio.
- Los tests usan solo los datos semilla ficticios (`@example.com`) y el almacén en memoria.
  No apuntes los tests a datos ni servicios reales, y deja el estado limpio con `reset()`.
- No alteres contratos existentes (ruta, parámetros, forma de la respuesta, códigos de estado)
  sin justificación escrita y aprobación. Los tests actuales son la referencia del contrato.
- Los mensajes de error no deben exponer más datos de los necesarios.

## Flujo de trabajo obligatorio

1. **Analizar** — leer el código afectado y los tests; separar hechos de hipótesis.
2. **Proponer** — describir el cambio, los archivos y las decisiones abiertas; esperar aprobación
   antes de tocar código.
3. **Probar** — escribir primero los tests de los criterios de aceptación y verlos fallar.
4. **Implementar** — el cambio mínimo que los hace pasar, respetando las capas.
5. **Verificar** — `pytest`, cobertura y `ruff check .` en verde; informar del resultado real.
6. **Documentar** — actualizar `README.md` (tabla de endpoints) y la especificación en `docs/`.

## Fuera de límites

- `migrations/` y `legacy/` — no modificar. `legacy/user_lookup_v1.py` sigue importado por
  un job externo; no lo reutilices (compara emails distinguiendo mayúsculas).
