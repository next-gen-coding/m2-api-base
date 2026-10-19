# Reto M2 — Evidencias: `GET /users/search`

- **Rama:** `feature/reto-m2-ia`, partiendo de `7517640` (igual a `main`). Los cambios aún no están commiteados.
- **Fecha:** 2026-10-19.
- **Entorno:** `.venv` con Python 3.12.3, fastapi 0.143.0, pydantic 2.14.0, pytest 9.1.1,
  pytest-cov 7.1.0 y ruff 0.17.0.
- **Especificación completa:** [`reto-m2-especificacion.md`](reto-m2-especificacion.md).

**Medido**: el resultado sale de un comando ejecutado. **Objetivo**: lo que se pedía.
**Limitación**: lo que no se verificó o se verificó solo en parte.

---

## 1. Objetivo y criterios de aceptación

**Objetivo:** buscar un usuario por email. Debe devolver `200` con el usuario si existe,
`404` si nadie tiene ese email y `422` si el formato no es válido.

| ID | Criterio | Estado medido | Test(s) |
|---|---|---|---|
| CA1 | 200 con `User` completo | ✅ | `test_search_user_email_existente_devuelve_200` |
| CA2 | Sin distinguir mayúsculas | ✅ | `test_search_user_ignora_mayusculas_devuelve_200` (×2), `test_search_user_encuentra_email_guardado_con_mayusculas` |
| CA3 | 404 si no existe | ✅ | `test_search_user_email_inexistente_devuelve_404`, `test_search_user_no_hace_coincidencias_parciales_devuelve_404` (×3) |
| CA4 | 422 por formato inválido, parámetro ausente o vacío | ✅ | `test_search_user_email_invalido_devuelve_422` (×3), `test_search_user_sin_parametro_devuelve_422`, `test_search_user_mas_sin_codificar_devuelve_422` |
| CA5 | `/{user_id}` no captura `/search` | ✅ | aserciones de `loc == ["query","email"]` en los tests de 422 |
| CA6 | Endpoints existentes sin cambios | ✅ | los 6 tests originales, sin ninguna línea modificada (`git diff`: 113 añadidas, 0 borradas) |
| CA7 | Un usuario recién creado se puede buscar | ✅ | `test_search_user_encuentra_usuario_recien_creado` |
| CA8 | Suite verde, ruff limpio, cobertura ≥ 80 % | ✅ | ver §6 y §7 |

## 2. Patrón de generación elegido

**Especificación primero y luego test-first (TDD):** análisis, especificación, tests en
rojo, implementación mínima, verificación, refactor y documentación.

Por qué este patrón:
- **La especificación evita decisiones implícitas.** Los casos límite de la §6 de la spec
  se observaron ejecutando código, no se supusieron.
- **Los tests en rojo comprueban que fallan por el motivo correcto.** En este repo era
  crítico: antes de implementar, `/users/search` ya respondía `422` porque la capturaba
  `/{user_id}`. Un test de 422 que solo mirara el status habría pasado en falso.
- **La implementación queda acotada** a lo que piden los tests: 10 líneas de código productivo.

## 3. Prompts utilizados e iteraciones

Cada iteración partió de un prompt del autor (aquí resumido). Todos pedían separar hechos
de hipótesis y no inventar resultados.

| # | Prompt (resumen) | Qué se hizo | Archivos tocados |
|---|---|---|---|
| 1 | Analizar el repo sin modificar nada: stack, estructura, tests, comandos, estado; 3 propuestas | Lectura completa, `pytest` (6 passed), cobertura, `ruff`, pruebas manuales de casos límite; 3 propuestas (PATCH, search, paginación) | ninguno |
| 2 | Especificar la funcionalidad B (search) sin implementar; señalar decisiones | Prueba desechable de `EmailStr` en la query (en el scratchpad); spec con CA1–CA8 y decisiones D1–D6 | ninguno (el autor guardó la spec en `docs/`) |
| 3 | Preparar `CLAUDE.md` solo con lo verificado, conservando lo válido | Reescritura del original; se verificó antes el comando de cobertura acotada | `CLAUDE.md` |
| 4 | Test-first: solo pruebas, ejecutarlas y registrar el motivo real de cada fallo | 15 casos nuevos; 15 failed y 6 passed, con el motivo comprobado caso por caso | `tests/test_users.py` |
| 5 | Implementar lo mínimo por etapas | Servicio (2 passed) → ruta (21 passed) → lint, cobertura y OpenAPI → README | `users/service.py`, `users/routes.py`, `README.md` |
| 6 | Analizar la cobertura real (líneas y ramas), añadir solo tests justificados | Medición con `--cov-branch`; 2 tests nuevos; 1 mutante manual | `tests/test_users.py` |
| 7 | Debugging de un fallo en `test_users.py` | No se pudo reproducir ningún fallo (ver §8); no se modificó nada | ninguno |
| 8 | Refactor pequeño y seguro, con aprobación | Se quitó el `str(email)` sobrante; la suite da lo mismo antes y después | `users/routes.py` |
| 9 | Documentación técnica con evidencias | Docstrings, README, CHANGELOG y este documento; prueba real con `uvicorn` | `users/*.py`, `README.md`, `CHANGELOG.md`, `docs/reto-m2-evidencias.md` |

## 4. Decisiones de la IA: aceptadas y rechazadas

**Aplicadas.** D1–D5 quedaron como las recomendó la IA. El autor no las aprobó una por una:
continuó el flujo sin objetarlas.

| Decisión | Resultado | Razón |
|---|---|---|
| D1 · Validar con `EmailStr` en la query (422 de Pydantic) | Aplicada | Reutiliza el tipo de `UserBase` y da el mismo 422 que `POST /users` |
| D2 · `service.get_user_by_email` + ruta `search_user` | Aplicada | En línea con `get_user` |
| D3 · Respuesta: un `User`, no una lista | Aplicada | El README dice "200 con el usuario" |
| D4 · Tests unitarios en `tests/test_users.py` | Aplicada | Convención de un archivo por recurso |
| D5 · No testear el parámetro repetido (gana el último) | Aplicada | Sin requisito que lo pida |
| D6 · Arreglar en este reto que se acepten nombres en blanco | **Rechazada** (aplazada) | Toca `schemas.py` y `POST /users`: queda fuera de alcance |
| Refactor: quitar `str(email)` | **Aprobada explícitamente** por el autor | Se comprobó que `EmailStr` entrega un `str` exacto |
| Refactor: helper `_search_user` en los tests | **No elegida** por el autor | Abstracción que el estilo de tests actual no usa |
| Extraer el patrón "buscar o 404" común a `get_user` y `get_user_by_email` | **Descartada** por la IA | Con dos usos sería una abstracción innecesaria (`CLAUDE.md`) |
| Test directo de `errors.invalid_request` | **Descartado** por la IA | Subiría la cobertura sin probar ningún comportamiento real |
| Aplicar `ruff format` al repo | **Descartado** | Reformatearía 8 archivos ajenos a la tarea |
| Consultar la rama `origin/solucion-clase1` | **No se consultó** | Para que el reto sea trabajo propio |

## 5. Resultados de las pruebas (medidos)

| Momento | Comando | Resultado |
|---|---|---|
| Inicial (repo base) | `pytest` | 6 passed |
| Tests nuevos, antes de implementar | `pytest -rfE --tb=line` | **15 failed, 6 passed** |
| Etapa 1: servicio | `pytest -k get_user_by_email` | 2 passed |
| Etapa 2: ruta | `pytest` | 21 passed |
| Tras el análisis de cobertura | `pytest` | 23 passed |
| Antes y después del refactor | `pytest` | 23 passed / 23 passed |
| Tras los docstrings | `pytest` y `ruff check .` | 23 passed; All checks passed! |

Motivo de los 15 fallos en rojo, comprobado llamando al endpoint con cada entrada:
- 13 casos HTTP: el servidor respondía `422 int_parsing` con `loc ["path","user_id"]`. Era
  la colisión con `/{user_id}`: la ruta todavía no existía.
- 2 unitarios: `AttributeError: module 'users.service' has no attribute 'get_user_by_email'`.

No hubo errores de configuración.

**Prueba manual con `uvicorn`** (medida en la iteración 9): servidor en `127.0.0.1:8765`.
- `/health`: 200.
- Búsqueda en minúsculas y en mayúsculas: 200.
- Email inexistente: 404.
- `no-es-email` y parámetro ausente: 422.
- Usuario creado con `POST` y buscado con `%2B` en el email: 201 y luego 200.

Los ejemplos están en el `README.md`.

## 6. Cobertura (medida)

Comando: `pytest --cov=users --cov=core --cov=main --cov-branch --cov-report=term-missing`

| Momento | Líneas | Ramas | Combinado |
|---|---|---|---|
| Repo base, `--cov=.` (incluye `tests/`) | 111/113 (98 %) | no medido | — |
| Repo base, sin `tests/` | 71/73 (97 %) | no medido | — |
| Final, sin `tests/` | **80/82 (97,56 %)** | **8/8 (100 %)** | 97,78 % |

- **Objetivo:** ≥ 80 %. Se supera en líneas y en ramas.
- **Líneas sin cubrir:** `core/errors.py:20` (`invalid_request`, que no se usa) y
  `main.py:16` (`/health`, sin test). Ninguna pertenece al reto.
- `users/routes.py` y `users/service.py` están al 100 %.
- **Limitación:** coverage.py no mide ramas dentro del generador de
  `repository.find_by_email`. Su 100 % de ramas no garantiza que esa condición esté bien probada.
- **Limitación:** no se comprobó qué métrica exacta usa la rúbrica.

## 7. Mutation testing

**Se ejecutó de forma manual con un único mutante.** No se usó ninguna herramienta de mutación
(no hay `mutmut` ni similar en `requirements.txt`), así que no existe un *mutation score*.

- **Mutante:** `repository.find_by_email`, reemplazado en memoria (sin tocar archivos) por una
  versión que pasa a minúsculas solo la consulta, no el email guardado.
- **Resultado medido:** 22 passed, **1 failed**. Solo lo detectó el test añadido en la
  iteración 6, `test_search_user_encuentra_email_guardado_con_mayusculas` (`assert 404 == 200`).
- **Conclusión:** antes de la iteración 6 ese mutante sobrevivía a toda la suite. El hueco era
  real y está cerrado.

## 8. Diagnóstico de bugs y refactorización

**Debugging (iteración 7).** Se pidió analizar "un fallo real" de `test_users.py` sin adjuntar
traceback. Se ejecutó la suite de seis formas:
- con el ejecutable `pytest` del venv;
- con el comando de cobertura del README;
- cada test por separado (23 ejecuciones);
- en orden inverso;
- desde `tests/`;
- con el Python global.

Resultado medido:
- En todas las variantes con el `.venv`, 23 passed.
- Con el Python global: `No module named pytest`. Causa: el intérprete está fuera del venv.
  Arreglo: usar `.venv`, sin cambiar código.
- No se inventó un diagnóstico para un fallo que no se pudo reproducir.

**Defectos reales observados, aún no corregidos:**
- `POST /users` acepta `name: "   "` (201). Queda aplazado (D6).
- El 409 repite el email tal como lo envió el cliente, no el que está guardado.
- El 404 de la búsqueda repite el email consultado: permite comprobar qué emails están registrados.

**Refactorización (iteración 8):**
- **Problema:** `str(email)` no hacía nada y daba a entender que el valor no era un `str`.
- **Cambio:** de `service.get_user_by_email(str(email))` a `service.get_user_by_email(email)`.
- **Verificación:** 23 passed antes y después, la misma cobertura y el linter limpio. Afecta a
  una sola línea de `users/routes.py`.
- **Riesgo residual:** `create_user` mantiene `str(data.email)`, código anterior al reto.

## 9. Reflexión personal y mejoras futuras

### Reflexión personal
> *A completar por el autor.* Sugerencias: qué aportó la IA y dónde hubo que corregirla,
> qué decisiones habrías tomado distinto (p. ej. D1), qué aprendiste del ciclo test-first.

### Observaciones técnicas del proceso (respaldadas por la evidencia anterior)
- Ejecutar el código antes de especificar evitó errores en la spec. Por ejemplo, un `+` sin
  codificar llega como espacio y `EmailStr` quita los espacios de los extremos.
- Hacer que las aserciones de 422 comprueben `loc` fue lo que hizo útiles esos tests.
- Una cobertura del 97–100 % no bastó por sí sola: hizo falta un mutante para encontrar un hueco.

### Mejoras futuras
- Corregir la aceptación de nombres en blanco en `UserBase`, con un test de regresión (D6).
- Decidir si los 422 de formato deben salir del catálogo en español (`invalid_request`), según
  la convención de `CLAUDE.md`.
- Declarar el `404` en `responses=` para que aparezca en OpenAPI. Hoy solo figuran 200 y 422,
  igual que en `GET /users/{user_id}`.
- Añadir un test de humo para `GET /health`.
- Hacer mutation testing sistemático con una herramienta. Requiere aprobar una dependencia nueva.
- Fijar las versiones de las dependencias (lock): `requirements.txt` solo pone mínimos.
