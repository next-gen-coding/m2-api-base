# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).
La versión del proyecto sigue siendo `0.1.0` (`pyproject.toml`, `main.py`): estos cambios
aún no tienen versión ni tag asignados.

## [Sin publicar] — 2026-10-19 · rama `feature/reto-m2-ia`

### Añadido
- `GET /users/search?email=<email>`: devuelve un único `User` buscando por email exacto,
  sin distinguir mayúsculas. Responde `404` si no existe y `422` si el email falta o no es válido.
  - `users/routes.py`: ruta `search_user`, declarada antes de `/users/{user_id}`.
  - `users/service.py`: `get_user_by_email`, que reutiliza `repository.find_by_email` y
    `errors.not_found`.
- 17 casos de test nuevos en `tests/test_users.py` (15 de integración y 2 unitarios del servicio).
- Docstrings en las funciones públicas de `users/routes.py`, `users/service.py` y en
  `repository.find_by_email`.
- `docs/reto-m2-especificacion.md` y `docs/reto-m2-evidencias.md`.

### Cambiado
- `README.md`: fila del nuevo endpoint, uso y ejemplos HTTP, activación en PowerShell,
  comando de cobertura con ramas y último resultado medido.
- `CLAUDE.md`: reescrito a partir del original, conservando sus reglas. Añade versiones
  verificadas, reglas por capa, estrategia de pruebas, seguridad y flujo de trabajo.

### Sin cambios
- Los contratos de `GET /health`, `GET /users`, `GET /users/{user_id}` y `POST /users`.
  Los 6 tests anteriores siguen pasando sin modificaciones.
- Dependencias: ninguna nueva.
