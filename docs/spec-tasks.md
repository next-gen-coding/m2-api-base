# Spec: recurso tasks (reto M2)

**Objetivo:** que el equipo registre y consulte sus tareas operativas, para que no se pierda trabajo sin registrar (objetivo del sprint).

**Alcance:** crear y consultar tareas.
**Fuera de alcance:** editar, borrar, listar y usuarios asignados.

## Endpoints

- `POST /tasks` — crear una tarea.
- `GET /tasks/{task_id}` — consultar una tarea.

## Datos para crear una tarea

| Campo      | Qué es             | Regla                                                  |
|------------|--------------------|--------------------------------------------------------|
| `title`    | Nombre de la tarea | Obligatorio, de 3 a 100 caracteres, no solo espacios   |
| `priority` | Urgencia           | Entero del 1 (baja) al 5 (alta)                        |
| `due_date` | Fecha límite       | Formato `AAAA-MM-DD`; hoy o una fecha futura           |

Header opcional: `Idempotency-Key` (texto) para evitar duplicados.

## Criterios de aceptación

| #   | Criterio                                                            | Respuesta esperada                                                     |
|-----|---------------------------------------------------------------------|------------------------------------------------------------------------|
| CA1 | Crear una tarea con datos válidos                                   | **201** con `id`, `title`, `priority`, `due_date`, `status: "pending"` |
| CA2 | Título vacío, solo espacios, de menos de 3 o más de 100 caracteres  | **422**, no se crea nada                                               |
| CA3 | Prioridad 0, 6 o que no es número                                   | **422**                                                                |
| CA4 | Fecha límite anterior a hoy (hoy sí se acepta)                      | **422** con mensaje en español                                         |
| CA5 | Mismo envío repetido con el mismo `Idempotency-Key`                 | Regresa la tarea original, sin duplicar                                |
| CA6 | Consultar una tarea existente / inexistente                         | **200** con la tarea / **404** con mensaje en español                  |
| CA7 | Formato y errores                                                   | Siempre schemas Pydantic; errores desde `core/errors.py`               |
| CA8 | Calidad                                                             | Los 6 tests previos pasan, `ruff check .` limpio, cobertura de `tasks` >90% (líneas y ramas), mutantes manuales detectados |

## Ejemplo

Petición:

    POST /tasks
    Idempotency-Key: abc-123
    {"title": "Revisar respaldo nocturno", "priority": 4, "due_date": "2026-11-15"}

Respuesta 201:

    {"id": 1, "title": "Revisar respaldo nocturno", "priority": 4, "due_date": "2026-11-15", "status": "pending"}