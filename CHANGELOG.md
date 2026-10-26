# Changelog

Todos los cambios relevantes de este proyecto se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y el proyecto usa [Versionado Semántico](https://semver.org/lang/es/).

## [0.2.0] - 2026-10-25

### Added

- Recurso `tasks` para registrar y consultar tareas operativas, con el mismo patrón
  de capas que `users/` (`routes.py`, `service.py`, `schemas.py`, `repository.py`
  en memoria) y su especificación en `docs/spec-tasks.md`.
- `POST /tasks`: crea una tarea y responde 201 con `status: "pending"`.
  Valida el formato del título (3 a 100 caracteres) y de la prioridad (1 a 5).
- `POST /tasks` responde 422 con mensaje en español cuando la fecha límite ya pasó;
  la fecha de hoy sí se acepta.
- `GET /tasks/{task_id}`: consulta una tarea; responde 404 si no existe.
- Idempotencia en `POST /tasks` con el header `Idempotency-Key`: repetir el envío
  con la misma clave devuelve la tarea original sin crear un duplicado.
- Tests del recurso `tasks`: criterios CA1–CA6 por HTTP (`tests/test_tasks.py`) y
  unitarios del service con el repositorio simulado (`tests/test_tasks_service.py`).
- `users/validation.py`: utilidades puras de validación de `users`, todavía sin tests
  (base de la Clase 2).

### Fixed

- `POST /tasks` aceptaba un título formado solo por espacios; ahora responde 422.
- `POST /tasks` aceptaba `true`/`false` como prioridad (Pydantic los convertía en
  1 y 0); ahora responde 422.
- `POST /tasks` aceptaba títulos como `"  ab "` porque el mínimo de 3 caracteres
  contaba los espacios de los extremos; ahora responde 422. El título se sigue
  guardando tal como llega.

### Changed

- `core.errors.not_found` acepta el argumento opcional `gender`
  (`"masculine"` por defecto, o `"feminine"`) para que el mensaje 404 concuerde con
  el recurso. Los mensajes actuales no cambian.
