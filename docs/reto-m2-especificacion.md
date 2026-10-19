Esta es la especificación de GET /users/search para que la revises. Todavía no he implementado nada y el repositorio sigue sin cambios.

Para no especificar a ciegas, probé cómo valida FastAPI un email que llega en la query con un script desechable fuera del repo. Lo que marco con [H] viene de esas pruebas o de leer el código. Al final hay seis decisiones que necesitan tu aprobación (D1–D6).

---

Especificación: GET /users/search?email=<email>

1. Objetivo y alcance

Objetivo: buscar un usuario a partir de su email.

Dentro del alcance:
- La ruta, la función de servicio y sus tests.
- Actualizar la tabla de endpoints del README.md.

Fuera del alcance:
- Búsquedas parciales o por nombre.
- Paginación.
- Cambios en POST /users.
- Cualquier cambio en legacy/ o migrations/.
- No hacen falta dependencias nuevas.

2. Criterios de aceptación

┌─────┬───────────────────────────────────────────┬────────────────┐
│ ID  │                 Criterio                  │    Cómo se     │
│     │                                           │    verifica    │
├─────┼───────────────────────────────────────────┼────────────────┤
│     │ Si el email existe, responde 200 con el   │ test de        │
│ CA1 │ User completo (id, name, email,           │ integración    │
│     │ created_at)                               │                │
├─────┼───────────────────────────────────────────┼────────────────┤
│ CA2 │ La búsqueda no distingue mayúsculas:      │ test           │
│     │ ADA@EXAMPLE.COM encuentra a id=1          │                │
├─────┼───────────────────────────────────────────┼────────────────┤
│     │ Si el email tiene un formato válido pero  │                │
│ CA3 │ nadie lo tiene, responde 404 con un       │ test           │
│     │ detail que contiene "no encontrado"       │                │
├─────┼───────────────────────────────────────────┼────────────────┤
│ CA4 │ Si el formato no es válido, falta el      │ tests          │
│     │ parámetro o viene vacío, responde 422     │                │
├─────┼───────────────────────────────────────────┼────────────────┤
│     │ /users/search no la captura /{user_id}:   │ test de        │
│ CA5 │ el 422 señala loc = ["query","email"], no │ regresión      │
│     │  ["path","user_id"]                       │                │
├─────┼───────────────────────────────────────────┼────────────────┤
│ CA6 │ GET /users/{user_id}, GET /users y POST   │ los 6 tests    │
│     │ /users siguen funcionando igual           │ actuales pasan │
├─────┼───────────────────────────────────────────┼────────────────┤
│ CA7 │ Un usuario creado con POST /users se      │ test de        │
│     │ puede buscar justo después                │ integración    │
├─────┼───────────────────────────────────────────┼────────────────┤
│     │ pytest pasa, ruff check . queda limpio y  │                │
│ CA8 │ la cobertura de users, core y main es de  │ comandos       │
│     │ al menos 80 %                             │                │
└─────┴───────────────────────────────────────────┴────────────────┘

3. Contrato HTTP

- Método y ruta: GET /users/search.
- Parámetro de query: email, obligatorio, de tipo EmailStr (ver D1).
- 200: response_model=User, un único objeto y no una lista (D3).
{"name": "Ada Lovelace", "email": "ada@example.com", "id": 1, "created_at": "..."}
- 404: {"detail": "usuario no encontrado: <email>"}, generado con errors.not_found("usuario", email).
- 422: el formato estándar de validación de FastAPI, por ejemplo {"detail":[{"type":"value_error","loc":["query","email"],...}]}.

4. Qué se reutiliza (todo existe ya) [H]

- users.schemas.User como modelo de respuesta.
- pydantic.EmailStr, ya usado en UserBase; email-validator ya está instalado.
- users.repository.find_by_email(email) -> User | None, que ya compara en minúsculas. No hay que tocar repository.py.
- core.errors.not_found.
- Fixtures client y _reset_data de tests/conftest.py.
- No se reutiliza legacy/user_lookup_v1.lookup: trabaja sobre JSON y compara distinguiendo mayúsculas.

5. Reglas de negocio y validaciones

1. La validación de formato ocurre en la capa HTTP, porque el parámetro es EmailStr.
2. La ruta no tiene lógica: llama a service.get_user_by_email(email) (nombre en D2).
3. El servicio llama a repository.find_by_email(str(email)). Si devuelve None, el servicio lanza errors.not_found("usuario", email); si no, devuelve el User.
4. La búsqueda no distingue mayúsculas en ninguna parte del email, porque ese es el comportamiento que ya tiene find_by_email y es el mismo criterio que usa el 409 de POST /users.

6. Casos límite (comportamiento observado con EmailStr en la query) [H]

┌────────────────────────────────┬─────────────────────────────────┐
│            Entrada             │            Resultado            │
├────────────────────────────────┼─────────────────────────────────┤
│ ?email=ada@example.com         │ 200, id 1                       │
├────────────────────────────────┼─────────────────────────────────┤
│                                │ 200, id 1. EmailStr pasa el     │
│ ?email=ADA@EXAMPLE.COM /       │ dominio a minúsculas pero       │
│ Ada@Example.COM                │ conserva el local;              │
│                                │ find_by_email resuelve el resto │
├────────────────────────────────┼─────────────────────────────────┤
│ ?email=%20ada@example.com%20   │ 200. EmailStr quita los         │
│                                │ espacios de los extremos        │
├────────────────────────────────┼─────────────────────────────────┤
│ ?email=no-es-email             │ 422 value_error                 │
├────────────────────────────────┼─────────────────────────────────┤
│ ?email= (vacío)                │ 422 value_error                 │
├────────────────────────────────┼─────────────────────────────────┤
│ sin parámetro                  │ 422 missing                     │
├────────────────────────────────┼─────────────────────────────────┤
│ ?email=ada@example (dominio    │ 422                             │
│ sin TLD)                       │                                 │
├────────────────────────────────┼─────────────────────────────────┤
│                                │ 422: el + llega como espacio.   │
│ ?email=a+b@example.com sin     │ Hay que enviarlo como %2B       │
│ codificar                      │ (client.get(..., params={...})  │
│                                │ lo codifica solo)               │
├────────────────────────────────┼─────────────────────────────────┤
│ ?email=a%2Bb@example.com       │ 200 si existe y 404 si no       │
├────────────────────────────────┼─────────────────────────────────┤
│ ?email=x&email=y (parámetro    │ 200 con el último valor, que es │
│ repetido)                      │  el comportamiento por defecto  │
│                                │ de FastAPI (D5)                 │
└────────────────────────────────┴─────────────────────────────────┘

7. Archivos

Para consultar: CLAUDE.md, README.md, users/routes.py, users/service.py, users/repository.py, users/schemas.py, core/errors.py, tests/conftest.py, tests/test_users.py y pyproject.toml.

Para modificar:
- users/routes.py: añadir @router.get("/search", response_model=User) antes de @router.get("/{user_id}"), e importar EmailStr y Query.
- users/service.py: añadir una función nueva.
- tests/test_users.py: añadir los tests.
- README.md: añadir una fila a la tabla de endpoints.

Sin cambios: repository.py, schemas.py, core/errors.py y main.py.

Archivos nuevos: ninguno, porque el proyecto usa un archivo de tests por recurso (D4).

8. Estrategia de pruebas

No hacen falta mocks: el almacén vive en memoria y _reset_data lo reinicia entre tests. Los tests siguen el estilo del archivo: nombres en español y bloques arrange/act/assert.

Integración (client):
- test_search_user_email_existente_devuelve_200 (CA1)
- test_search_user_ignora_mayusculas_devuelve_200 (CA2)
- test_search_user_email_inexistente_devuelve_404 (CA3)
- test_search_user_email_invalido_devuelve_422, parametrizado con no-es-email, "" y ada@example (CA4)
- test_search_user_sin_parametro_devuelve_422 (CA4)
- test_search_user_no_la_captura_get_user_por_id: comprueba que loc == ["query","email"] (CA5)
- test_search_user_encuentra_usuario_recien_creado: hace POST y luego search, con un email que lleve + para cubrir la codificación (CA7)

Unitarias (servicio llamado directamente):
- test_get_user_by_email_devuelve_el_usuario
- test_get_user_by_email_inexistente_lanza_404: pytest.raises(HTTPException) y comprobar status_code == 404

Cobertura:
pytest --cov=users --cov=core --cov=main --cov-report=term-missing
core/errors.py:20 (invalid_request) seguirá sin cubrir. Es esperable y no afecta al umbral del 80 %.

9. Riesgos de compatibilidad

1. Orden de rutas: es el riesgo principal. Si /search se declara después de /{user_id}, devuelve un 422 int_parsing, como ocurre hoy [H]. Lo cubre CA5.
2. Dos formatos de 422: el de Pydantic es una lista con mensajes en inglés, mientras que invalid_request devuelve texto en español. Es la misma situación que ya tiene POST /users, pero choca con la convención del CLAUDE.md de que los mensajes de error estén en español (D1).
3. El 404 repite el email recibido: permite comprobar qué emails están registrados. Se acepta en un ejercicio, pero hay que mencionarlo en la documentación.
4. El + sin codificar da 422. Es un problema del cliente, no un bug, pero conviene documentarlo.
5. Diferencia con legacy/user_lookup_v1.lookup, que distingue mayúsculas. No se toca ese módulo; solo hay que saber que los dos dan resultados distintos.
6. OpenAPI: aparece una operación nueva. No cambia ningún contrato existente ni añade dependencias.

---

Decisiones que necesitan tu aprobación

- D1. Dónde se valida el formato (afecta al formato del 422).
  - Mi recomendación es EmailStr en la query: reutiliza un tipo que ya existe y da el mismo 422 que POST /users.
  - La alternativa es recibir email: str y validar en service.py con errors.invalid_request("El email no tiene un formato válido"). Así el mensaje queda en español y se cubre invalid_request, pero hay que validar el email a mano.
- D2. Nombre de la función de servicio. Recomiendo get_user_by_email, en línea con get_user. La alternativa es search_user_by_email. La función de la ruta sería search_user.
- D3. Formato de la respuesta. Recomiendo un solo User, como dice el README ("200 con el usuario"), y no list[User].
- D4. Dónde van las unitarias. Recomiendo ponerlas en tests/test_users.py, siguiendo la convención de un archivo por recurso, y no en un tests/test_users_service.py nuevo.
- D5. Parámetro repetido. Recomiendo aceptar que gane el último valor, documentarlo y no testearlo. La alternativa (rechazarlo) añade complejidad sin un requisito que la pida.
- D6. Ampliar el alcance con el arreglo de nombres en blanco (hoy name: "   " devuelve 201). Recomiendo hacerlo en una tarea separada después, porque toca schemas.py y POST /users. También sirve como el ejercicio de debugging del reto.

Además, existe origin/solucion-clase1 con una solución hecha. Asumo que no la consultamos para que el reto sea trabajo propio; avísame si prefieres usarla como referencia al final.

Cuando apruebes o ajustes D1–D6, implemento siguiendo esta especificación.

✻ Cogitated for 1m 6s · done 8:49 AM
                                 ✔ Update installed · Restart to update
────────────────────────────