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

### Aceptar cambios 
git add -A && git commit -m "feat(tasks): crear y consultar tarea, happy path"

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


### Aceptar cambios

git add -A && git commit -m "feat(tasks): validar titulo y fecha pasada"

### No encontrado → 404 (CA6) - Prompt

si la tarea no existe, GET /tasks/{task_id} responde 404 usando
errors.not_found de @core/errors.py, levantado desde service.py. Corre `pytest -q`.

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

### Aceptar cambios

git commit -m "feat(tasks): idempotencia con Idempotency-Key"


### Terminar fecha pasada - prompt

En @tasks/service.py resuelve el TODO de fecha pasada: si due_date es anterior a
today, responde 422 con errors.invalid_request de @core/errors.py y un mensaje en
español (hoy sí se acepta). Respeta el orden actual: la clave de idempotencia se
revisa primero. Dime qué código de estado devuelve invalid_request.
Corre `pytest -q` y `ruff check .`.

### Respuesta

Resolví el TODO de fecha pasada en tasks/service.py. Si due_date es anterior a today, create_task levanta errors.invalid_request con este mensaje:

▎ La fecha límite 2026-10-23 ya pasó; debe ser hoy o una fecha futura.

La comparación es due_date < today, así que la fecha de hoy se acepta. Se comprueba después de la clave de idempotencia, en el orden que pediste.

errors.invalid_request devuelve 422 (HTTP_422_UNPROCESSABLE_CONTENT), en core/errors.py:18-23.

Resultados: pytest -q pasa los 6 tests y ruff check . pasa limpio.

Lo probé a mano fuera de pytest, fijando "hoy" en 2026-10-24 con app.dependency_overrides[get_today]:

┌────────────────────────────────────┬────────────┬──────────────────────────────────────┐
│                Caso                │  due_date  │              Resultado               │
├────────────────────────────────────┼────────────┼──────────────────────────────────────┤
│ Ayer                               │ 2026-10-23 │ 422 con el mensaje de arriba         │
├────────────────────────────────────┼────────────┼──────────────────────────────────────┤
│ Hoy                                │ 2026-10-24 │ 201                                  │
├────────────────────────────────────┼────────────┼──────────────────────────────────────┤
│ Mañana                             │ 2026-10-25 │ 201                                  │
├────────────────────────────────────┼────────────┼──────────────────────────────────────┤
│ Reenvío con clave ya usada, cuerpo │ 2026-10-01 │ 201 con la tarea original, por el    │
│  con fecha pasada                  │            │ orden clave → fecha                  │
└────────────────────────────────────┴────────────┴──────────────────────────────────────┘

Ya no quedan TODO de lógica en el service. Falta el de títulos de solo espacios en schemas.py, y faltan tests/test_tasks.py y el reset de tasks en conftest.py para CA8.

### Aceptar cambios
(.venv) PS D:\Next-Gen Coding 2026\Reto M2\m2-api-base> git commit -m "feat(tasks): 422 cuando la fecha limite ya paso"
[reto-m2-tasks 5318717] feat(tasks): 422 cuando la fecha limite ya paso
 2 files changed, 42 insertions(+), 2 deletions(-)

(.venv) PS D:\Next-Gen Coding 2026\Reto M2\m2-api-base> git commit -m "feat(tasks): 422 cuando la fecha limite ya paso"
[reto-m2-tasks 5318717] feat(tasks): 422 cuando la fecha limite ya paso
 2 files changed, 42 insertions(+), 2 deletions(-)

### Tests

Añade los tests de tasks siguiendo el estilo de @tests/test_users.py y
@docs/spec-task.md:
- En @tests/conftest.py, reinicia también tasks.repository entre tests.
- tests/test_tasks.py: un test por criterio CA1 a CA6, con TestClient,
  estructura Arrange–Act–Assert y nombres descriptivos en español.
  Para la fecha, sobrescribe get_today con una fecha fija (no uses la fecha real).
- Incluye un test de integración: crear una tarea y luego consultarla con GET.
Corre `pytest -q`.

### Respuesta

Los tests de tasks están escritos y pytest -q da 19 pasan, 1 falla. El que falla detecta un hueco real del código: un título de solo espacios ("   ") se acepta con 201 y debería dar 422. Es el TODO que quedó pendiente en tasks/schemas.py: hoy Field(min_length=3) cuenta los 3 espacios como caracteres válidos. No lo corregí porque pediste solo los tests. ruff check . pasa limpio.

tests/conftest.py: el fixture automático ahora reinicia tasks.repository además del de users, antes y después de cada test.

tests/test_tasks.py (14 casos):
- Un fixture automático fija "hoy" en 2026-10-24 con app.dependency_overrides[get_today] y lo quita al terminar. Ningún test usa la fecha real.

┌─────────────┬───────────────────────────────────────────────────────────────────────────────────┬─────────────────────┐
│  Criterio   │                                       Test                                        │    Qué comprueba    │
├─────────────┼───────────────────────────────────────────────────────────────────────────────────┼─────────────────────┤
│ CA1         │ test_create_task_valida_devuelve_201_con_status_pending                           │ 201 y el cuerpo     │
│             │                                                                                   │ completo exacto     │
├─────────────┼───────────────────────────────────────────────────────────────────────────────────┼─────────────────────┤
│             │ test_create_task_titulo_invalido_devuelve_422_y_no_crea_nada (4 variantes: vacío, │ 422, y que GET      │
│ CA2         │  solo espacios, menos de 3, más de 100)                                           │ /tasks/1 da 404 (no │
│             │                                                                                   │  se creó nada)      │
├─────────────┼───────────────────────────────────────────────────────────────────────────────────┼─────────────────────┤
│ CA3         │ test_create_task_prioridad_fuera_de_rango_devuelve_422 (0, 6, "alta")             │ 422 y que no se     │
│             │                                                                                   │ creó nada           │
├─────────────┼───────────────────────────────────────────────────────────────────────────────────┼─────────────────────┤
│ CA4         │ test_create_task_fecha_pasada_devuelve_422_con_mensaje_en_espanol                 │ 422 con el mensaje  │
│             │                                                                                   │ exacto              │
├─────────────┼───────────────────────────────────────────────────────────────────────────────────┼─────────────────────┤
│ CA4         │ test_create_task_fecha_de_hoy_se_acepta                                           │ 201 con la fecha de │
│             │                                                                                   │  hoy                │
├─────────────┼───────────────────────────────────────────────────────────────────────────────────┼─────────────────────┤
│             │                                                                                   │ Cuerpo igual al     │
│ CA5         │ test_create_task_misma_idempotency_key_devuelve_la_original_sin_duplicar          │ original, id 1, y   │
│             │                                                                                   │ GET /tasks/2 da 404 │
├─────────────┼───────────────────────────────────────────────────────────────────────────────────┼─────────────────────┤
│             │ test_get_task_existente_devuelve_200 /                                            │ 200 con la tarea /  │
│ CA6         │ test_get_task_inexistente_devuelve_404_con_mensaje_en_espanol                     │ 404 con el mensaje  │
│             │                                                                                   │ exacto              │
├─────────────┼───────────────────────────────────────────────────────────────────────────────────┼─────────────────────┤
│             │                                                                                   │ El GET devuelve     │
│ Integración │ test_crear_y_consultar_tarea_devuelve_los_mismos_datos                            │ exactamente lo que  │
│             │                                                                                   │ devolvió el POST    │
└─────────────┴───────────────────────────────────────────────────────────────────────────────────┴─────────────────────┘

CA2, CA3 y CA6 tienen varios casos cada uno. Usé parametrize o tests separados para que siga habiendo un caso por test, como en test_users.py.

El test del 404 compara el mensaje exacto "tarea no encontrado: 999". Si después cambias la plantilla de core/errors.py por la concordancia, habrá que actualizarlo.

La spec en docs/ se llama spec-tasks.md, no spec-task.md.

Si quieres, implemento el validador de solo espacios en schemas.py para que pasen los 20.

### Verificamos con pytest -q

(.venv) PS D:\Next-Gen Coding 2026\Reto M2\m2-api-base> pytest tests/test_tasks.py -k "titulo_invalido" -q
.F..                                                                               [100%]
======================================= FAILURES ========================================
______ test_create_task_titulo_invalido_devuelve_422_y_no_crea_nada[solo_espacios] ______

client = <starlette.testclient.TestClient object at 0x0000023243EA11D0>, title = '   '

    @pytest.mark.parametrize(
        "title",
        ["", "   ", "ab", "a" * 101],
        ids=["vacio", "solo_espacios", "menos_de_3", "mas_de_100"],
    )
    def test_create_task_titulo_invalido_devuelve_422_y_no_crea_nada(
        client: TestClient, title: str
    ) -> None:
        payload = {**VALID_PAYLOAD, "title": title}
    
        response = client.post("/tasks", json=payload)
    
>       assert response.status_code == 422
E       assert 201 == 422
E        +  where 201 = <Response [201 Created]>.status_code

tests\test_tasks.py:58: AssertionError
================================ short test summary info ================================
FAILED tests/test_tasks.py::test_create_task_titulo_invalido_devuelve_422_y_no_crea_nada[solo_espacios] - assert 201 == 422

### Debugging con método de clase 3 - Prompt

Este test falla:
test_create_task_titulo_invalido_devuelve_422_y_no_crea_nada, variante "solo espacios".
Qué esperaba: 422 con title "   " (CA2 de @docs/spec-tasks.md).
Qué obtengo: 201, la tarea se crea.
Archivos: @tasks/schemas.py @tests/test_tasks.py

Dame 2-3 hipótesis de la causa, de más a menos probable, y cómo confirmar cada una.
NO cambies código todavía.

### Respuesta

La causa más probable ya está confirmada: TaskCreate acepta "   " porque nada en el schema rechaza títulos de solo espacios. Para comprobarlo corrí solo inspecciones en Python, sin cambiar código.

Hipótesis 1 (la más probable, confirmada): min_length=3 cuenta los espacios como caracteres.
- Field(min_length=3, max_length=100) solo mide el largo de la cadena, y "   " mide exactamente 3. Pydantic no recorta espacios por defecto, y el validador de title es el TODO que quedó en tasks/schemas.py:28.
- Cómo confirmarla: construir el modelo directamente, sin pasar por HTTP: TaskCreate(title="   ", priority=4, due_date="2026-11-15").
- Resultado: se crea sin error, con title == '   ' y len == 3. Las únicas restricciones de title son [MinLen(3), MaxLen(100)]. El fallo está en el schema, no en la ruta ni en el service.

Hipótesis 2 (descartada como causa, pero relacionada): el modelo no tiene configurado el recorte de espacios.
- Con model_config = ConfigDict(str_strip_whitespace=True), Pydantic recortaría "   " a "" antes de aplicar min_length, y daría 422.
- Cómo confirmarla: mirar TaskCreate.model_config.
- Resultado: está vacío ({}), así que no hay recorte. Es el mismo hueco que la hipótesis 1, visto desde la configuración y no desde el campo.

Hipótesis 3 (la menos probable, descartada): la ruta valida con otro modelo o el test no envía lo que parece.
- Pudo ocurrir que POST /tasks usara otro schema, o que el parametrize mandara otro valor.
- Cómo confirmarla: revisar qué modelo valida el cuerpo de la ruta y qué title se guardó.
- Resultado: la ruta usa tasks.schemas.TaskCreate, y el título llega intacto a la hipótesis 1. Las variantes "vacío", "menos de 3" y "más de 100" sí dan 422, lo que también confirma que la ruta valida con TaskCreate.

Cómo arreglarlo, cuando quieras:
- Opción A (recomendada): un field_validator("title") que rechace la cadena si title.strip() queda vacío. Cumple CA2 sin cambiar el contenido de los títulos válidos.
- Opción B: poner str_strip_whitespace=True en model_config. También funciona, pero modifica los títulos válidos: "  Revisar  " se guardaría como "Revisar". Además, " ab " pasaría a dar 422.

### Confirmación de hipótesis # 1

Confirmé la hipótesis número 1 leyendo la línea 24 title: str = Field(min_length=3, max_length=100). Aplica el fix mínimo en @tasks/schemas.py, nada más.
No toques los tests ni otras partes del código. Corre `pytest -q` y `ruff check .`.

### Respuesta

 Read 1 file

● Update(tasks\schemas.py)
Added 23 lines, removed 1 line
    priority: int = Field(ge=1, le=5)
    due_date: date

    # TODO: rechazar títulos de solo espacios (validador de campo sob
re `title`).
    @field_validator("title")
    @classmethod
    def reject_blank_title(cls, title: str) -> str:
        """Rechaza títulos formados solo por espacios.

        Args:
            title: Título recibido, ya validado en largo.

        Returns:
            El título sin modificar.

        Raises:
            ValueError: Si el título queda vacío al quitarle los espa
cios.

        Example:
            >>> TaskCreate(title="   ", priority=1, due_date=date(202
6, 11, 15))
            Traceback (most recent call last):
            ...
            pydantic_core._pydantic_core.ValidationError: ...
        """
        if not title.strip():
            raise ValueError("el título no puede estar formado solo p
or espacios")
        return title


class TaskOut(BaseModel):
    """Tarea tal como la devuelve la API.


● Update(tasks\schemas.py)
Added 1 line, removed 1 line
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field
from pydantic import BaseModel, Field, field_validator

TaskStatus = Literal["pending"]


  Ran 1 shell command

Un título de solo espacios ahora da 422: agregué un validador en tasks/schemas.py y ya pasan los 20 tests. ruff check . pasa limpio. No toqué los tests ni ninguna otra parte del código.

Qué cambié en tasks/schemas.py:
- Agregué field_validator al import de Pydantic.
- Agregué a TaskCreate un validador llamado reject_blank_title. Si title.strip() queda vacío, lanza ValueError("el título no puede estar formado solo por espacios"), y Pydantic lo convierte en una respuesta 422.
- Quité el TODO, porque ya está resuelto.
- El título válido se guarda tal cual llega, sin recortar espacios.
- Field(min_length=3, max_length=100) en la línea 24 se queda igual. El validador se ejecuta después del chequeo de largo.

El validador lleva un docstring estilo Google con ejemplo, que es más largo que el código. Lo puse porque CLAUDE.md lo pide para las funciones públicas de tasks/. Si quieres un cambio más corto, lo dejo en una línea.

### Comprobación con pytest -q

(.venv) PS D:\Next-Gen Coding 2026\Reto M2\m2-api-base> pytest tests/test_tasks.py -k "titulo_invalido" -q
....                                                                                        [100%]

### Aceptar cambio incremental

git commit -m "test(tasks): tests CA1-CA6 y fix de titulo con solo espacios"

## 3. Tests y cobertura (antes: 0% en tasks → después: __%; mutantes)
## 4. Debugging y refactorización
## 5. Documentación y reflexión

