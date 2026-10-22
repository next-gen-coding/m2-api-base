# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

## [0.2.0] - 2026-10-22

### Added

- Recurso `tasks` con CRUD completo: POST (201), GET lista (200), GET detalle (200), DELETE (204), PATCH (200).
- Validaciones de dominio: prioridad 1-5, título 1-120 chars, descripción opcional max 500, fecha futura obligatoria.
- Spec y criterios de aceptación en `docs/spec-tareas.md`.
- Tests de aceptación CA01-CA22 con boundary y edge cases.
- Tests unitarios de `tasks/service.py` con mocks (unittest.mock).
- Tests de integración (flujo completo usuario + tarea vía HTTP).
- Test de título con solo espacios (422).
- Test unitario con monkeypatch para fijar `date.today()`.
- Documentación de `tasks` en CLAUDE.md con reglas de dominio y convenciones.

### Changed

- Refactor: extraer `date.today()` a función `today()` en `tasks/service.py` para facilitar testing.
- README actualizado con endpoints de tasks, sección de recurso y comando de cobertura branch.

### Fixed

- Schema `TaskBase`: rechaza títulos compuestos solo de espacios (`field_validator`).

## [0.1.0] 

### Added

- Repo base: API REST de usuarios con FastAPI + Pydantic v2.
- Endpoints: GET `/health`, GET/POST `/users`, GET `/users/{id}`.
- Almacén en memoria con datos semilla.
- Suite de tests y linter (ruff).
