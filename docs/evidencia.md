(.venv) PS D:\Next-Gen Coding 2026\Reto M2\m2-api-base> pytest -q                      
......                                                                                                                                                                               [100%]
(.venv) PS D:\Next-Gen Coding 2026\Reto M2\m2-api-base> ruff check
All checks passed!


(.venv) PS D:\Next-Gen Coding 2026\Reto M2\m2-api-base> pytest --cov=users.routes --cov-report=term-missing    
......                                                                               [100%]
===================================== tests coverage ======================================
_____________________ coverage: platform win32, python 3.14.8-final-0 _____________________

Name              Stmts   Miss  Cover   Missing
-----------------------------------------------
users\routes.py      13      0   100%
-----------------------------------------------
TOTAL                13      0   100%
6 passed in 0.21s                     

# Evidencia — Reto M2
## 1. Especificación y contexto

Objetivo: que el equipo registre y consulte sus tareas operativas, para que no se pierda trabajo sin registrar (es el objetivo del sprint).
Alcance: crear y consultar tareas. Fuera de alcance: editar, borrar, listar y usuarios asignados.

Criterios de aceptación 

## 2. Generación de código (prompts, qué acepté y qué rechacé)
### Prompt
❯ Lee @CLAUDE.md, @users/routes.py, @users/service.py, @users/repository.py,
  @users/schemas.py, @core/errors.py y @tests/test_users.py.
  Resúmeme en 5 líneas las convenciones del proyecto y qué archivos usarías como
  ejemplo para añadir un endpoint nuevo al recurso users. No cambies nada.


### Respuesta
Convenciones (5 líneas):

1. Cada recurso tiene cuatro capas: routes.py → service.py → repository.py, más schemas.py. La ruta solo delega en el service, y solo el service habla con el repositorio.
2. Las rutas siempre declaran response_model= y devuelven modelos Pydantic, nunca dict. Los modelos de entrada terminan en *Create/*Update.
3. Los errores se levantan solo en el service, con core/errors.py (not_found, invalid_request, already_exists). Nunca se usa HTTPException a mano.
4. Los identificadores van en inglés y snake_case, sin abreviaturas. Los mensajes de error y los nombres de los tests van en español. Las rutas específicas (/users/search) se declaran antes que las que llevan parámetro (/users/{user_id}).
5. Cada endpoint nuevo lleva sus tests en tests/test_users.py: al menos un caso feliz y uno de error, uno por caso, con arrange/act/assert separados. No se tocan migrations/ ni legacy/.

Archivos que se usarían como ejemplo para un endpoint nuevo en users:

- users/routes.py:22-24 (get_user) es el modelo de ruta con parámetro y response_model. :27-29 (create_user) sirve para un POST con
  status_code.
- users/service.py:12-16 (get_user) muestra la búsqueda más la decisión de error con errors.not_found. :23-26 muestra una validación de
  negocio con already_exists.
- users/repository.py:43-45 (find_by_email) es la plantilla para una consulta nueva sobre el dict.
- users/schemas.py sirve si el endpoint necesita un mod.
- tests/test_users.py:18-29 es la pareja de test feliz (200) y de error (404) que hay que replicar.
- CLAUDE.md también tiene una sección sobre un recurso tasks (reto M2) con reglas extra: docstrings estilo Google, la fecha "hoy" inyectada como dependencia, idempotencia y cobertura >90%. Esas reglas aplican a tasks/, no a users/. No he modificado nada.

### Esqueleto
### Prompt
Quiero crear el recurso tasks con POST /tasks y GET /tasks/{task_id}, según
@docs/spec-task.md, siguiendo el patrón de @users/ y las convenciones de @CLAUDE.md.
Dame solo el ESQUELETO: la carpeta tasks/ con routes.py, service.py, schemas.py y
repository.py (firmas y tipos), y el registro del router en @main.py.
Pon un TODO donde irían la validación de fecha pasada, la idempotencia y el caso
"no encontrado". NO implementes lógica todavía.
Dime qué código de estado devuelve errors.invalid_request en @core/errors.py.

### Respuesta

El esqueleto de tasks/ ya está creado y el router está registrado en main.py. Sin ninguna lógica implementada, ruff check . pasa limpio y los 6 tests existentes siguen en verde. Los endpoints responden 500 por ahora: todo cuerpo pendiente lanza NotImplementedError.

El archivo se llama docs/spec-tasks.md, no spec-task.md. Usé ese.

Qué contiene cada archivo:
- tasks/schemas.py:
  - TaskCreate lleva title (3–100 caracteres), priority (1–5) y due_date: date. Los límites de largo y rango ya están declarados con Field, como pide CLAUDE.md.
  - TaskOut lleva id, title, priority, due_date y status: Literal["pending"].
  - Dejé un TODO extra: rechazar títulos que sean solo espacios. La spec lo pide en CA2 y Field no lo cubre.
- tasks/repository.py: un dict de tareas y otro de clavunciones están solo con firma: add, get,

### Verificación

| Campo      | Qué es             | Regla                                                  |
|------------|--------------------|--------------------------------------------------------|
| `title`    | Nombre de la tarea | Obligatorio, de 3 a 100 caracteres, no solo espacios   |
| `priority` | Urgencia           | Entero del 1 (baja) al 5 (alta)                        |
| `due_date` | Fecha límite       | Formato `AAAA-MM-DD`; hoy o una fecha futura           |

Los 4 archivos creados están en tasks/ y no se tocó users/.	
En main.py se agregó app.include_router(tasks_routes.router).
Las dos rutas incluyen: response_model=TaskOut.
Las dos rutas solo llaman a service.create_task y service.get_task. 
El POST devuelve 201: status_code=status.HTTP_201_CREATED.
Todas las funciones creadas dicen raise NotImplementedError. Hay dos excepciones aceptables:

En schemas.py ya puso las reglas del título (3 a 100 caracteres) y de la prioridad (1 a 5). Son declaraciones de una línea, no lógica compleja, así que las acepté.
En routes.py ya escribió get_today(), que devuelve la fecha de hoy. Es correcto que esté ahí y no en service.py.

pytest -q
[100%]
(.venv) PS D:\Next-Gen Coding 2026\Reto M2\m2-api-base> ruff check
All checks passed!


### Implementación incremental - Prompt 
implementa solo el happy path de @tasks/: repository.add, get y reset;
service.create_task crea la tarea con status "pending" y service.get_task la devuelve.
Sin validar fecha pasada, sin idempotencia y sin manejar "no encontrado" todavía.
Corre `pytest -q`.

### Respuesta
El happy path de tasks/ ya funciona. pytest -q pasa los 6 tests, pero todos son de users: tasks todavía no tiene ninguno. ruff check . pasa limpio.

Qué implementé:
- repository.add crea la tarea con id incremental y status="pending" y la guarda en el dict.
- repository.get devuelve la tarea o None.
- repository.reset vacía las tareas y las claves de idempotencia y reinicia el id a 1.
- service.create_task llama a repository.add y service.get_task a repository.get. Los TODO de fecha pasada, idempotencia y no encontrado siguen en su lugar.

Prueba a mano: hice una llamada fuera de pytest con el ejemplo de la spec:
- POST /tasks devolvió 201 con {"id": 1, "title": "Revisar respaldo nocturno", "priority": 4, "due_date": "2026-11-15", "status": "pending"}, igual que CA1.
- GET /tasks/1 devolvió 200 con esa misma tarea.

Pendiente para los siguientes pasos:
- Id inexistente: GET /tasks/999 hoy responde 500, no 404. get_task devuelve None y FastAPI no puede convertirlo en TaskOut. Se corrige al implementar el TODO de "no encontrado".
- Reset entre tests: tests/conftest.py solo reinicia el repositorio de users. Cuando escribamos tests/test_tasks.py habrá que llamar también a tasks.repository.reset(), o los ids se arrastrarán de un test a otro.


### Validaciones -> 422 (CA4 y CA2)

Rechaza títulos de solo espacios en @tasks/schemas.py y, en @tasks/service.py,
si due_date es anterior a today responde 422 con errors.invalid_request de
@core/errors.py (hoy sí se acepta). Confirma qué código devuelve invalid_request.
Corre `pytest -q`.

### Respuesta
GET /tasks/{task_id} ahora responde 404 cuando la tarea no existe. En service.get_task, si repository.get devuelve None, se levanta errors.not_found("tarea", task_id); quité ese TODO y agregué from core import errors. pytest -q pasa los 6 tests y ruff check . pasa limpio.

Lo probé a mano fuera de pytest: GET /tasks/999 devuelve 404 con {"detail": "tarea no encontrado: 999"}, y una tarea recién creada sigue devolviendo 200.

El mensaje tiene un error de concordancia: dice "tarea no encontrado". La plantilla de core/errors.py tiene fijo "no encontrado", que funciona para "usuario" pero no para "tarea". No lo cambié porque ese archivo lo usan todos los recursos. Hay dos formas de arreglarlo:
- Usar otro nombre de recurso: pasar "recurso tarea" en vez de "tarea". Solo cambia tasks/service.py, pero el mensaje queda raro.
- Ajustar core/errors.py: cambiar la plantilla a algo neutro como f"No se encontró {resource}: {identifier}". El mensaje de users cambia, pero su test ("no encontrado" in detail) se tendría que ajustar.

Además, falta lo que pide CLAUDE.md para este endpoint: aún no hay tests de tasks (caso feliz y caso 404) en tests/test_tasks.py.

### Idempotencia (CA5)

Si POST /tasks llega con un Idempotency-Key ya usado, devuelve la tarea
original sin crear otra (usa find_by_idempotency_key y save_idempotency_key de
@tasks/repository.py). Corre `pytest -q`.

### Respuesta
POST /tasks ya es idempotente: si llega con un Idempotency-Key ya usado, devuelve la tarea original y no crea otra. pytest -q pasa los 6 tests y ruff check . pasa limpio.

Qué cambié:
- repository.find_by_idempotency_key busca el id asociado a la clave y devuelve esa tarea, o None.
- repository.save_idempotency_key guarda la relación clave → id.
- service.create_task:
  - Si viene una clave ya registrada, devuelve la tarea original sin crear nada.
  - Si no, crea la tarea y, cuando hay clave, la registra.
  - Sin clave, cada POST crea una tarea nueva.
  - El TODO de fecha pasada sigue en su lugar.

Prueba a mano (fuera de pytest):

┌────────────────────────┬────────────────────────────────┐
│        Petición        │           Resultado            │
├────────────────────────┼────────────────────────────────┤
│ POST con abc-123       │ 201, id 1                      │
├────────────────────────┼────────────────────────────────┤
│ Mismo POST con abc-123 │ 201, id 1 (no se duplicó)      │
├────────────────────────┼────────────────────────────────┤
│ POST sin clave         │ 201, id 2                      │
├────────────────────────┼────────────────────────────────┤
│ GET /tasks/3           │ 404 (no hay una tercera tarea) │
└────────────────────────┴────────────────────────────────┘

Decisiones que tomé y puedes cambiar:
- Código del reenvío: responde 201, igual que la primera vez. La spec solo pide devolver la tarea original; si prefieres 200, hay que mover el código de estado de la ruta al service.
- Cuerpo distinto con la misma clave: devuelve la tarea original sin comparar el cuerpo. CA5 habla de "mismo envío", y la otra opción sería responder 409 con already_exists.
- Orden de las comprobaciones: la clave se revisa antes que la fecha. Un reenvío devolverá la original aunque su fecha ya haya pasado.

Todavía no hay tests de tasks. El de idempotencia necesitará el reset de tasks.repository en conftest.py para que el registro de claves no pase de un test a otro.

### Mi revisión

### Las 3 decisiones de Claude

| Decisión | Mi recomendación |
| :--- | :--- |
| El reenvío responde 201 | ✅ **Aceptarla.** Repetir la misma respuesta que la primera vez es lo normal en APIs idempotentes, y es más simple. |
| Cuerpo distinto con la misma clave → devuelve la original | ✅ **Aceptarla**, pero agregarla como limitación conocida en el README. CA5 habla de “mismo envío”, así que cumple. |
| La clave se revisa antes que la fecha | ✅ **Aceptarla**, es correcto. Si alguien reenvía una tarea que ya se creó, debe recibir la original aunque la fecha ya haya pasado. |



## 3. Tests y cobertura (antes: 0% en tasks → después: __%; mutantes)
## 4. Debugging y refactorización
## 5. Documentación y reflexión

