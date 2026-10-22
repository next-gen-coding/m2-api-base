USR-143 Implementación de tasks  Prioridad: alta  Pidió: Soporte  Revisa: QA

Contexto: Permitir que el equipo registre tareas operativas asignadas a un usuario existente, para que ningún trabajo quede sin registrar y las tareas tengan un responsable.

Criterios de aceptación:
1. POST /tasks/ crea la tarea asignada a un usuario (201).
2. GET /tasks/{task_id} retorna una tarea (200).
3. GET /tasks/ retorna la lista de tareas existentes (200).
4. Debe dar un error 404 si el usuario asignado no existe al crear la tarea.
5. DELETE /tasks/{task_id} permite eliminar una tarea (204).
6. PATCH /tasks/{task_id} permite actualizar la tarea; solo puede cambiar user_id y/o status.
7. Los status permitidos son todo, in_progress, done. Las transiciones entre estados son libres.
8. Los campos del POST son title, description, priority, user_id, due_date. El response regresa todos los campos: id, title, description, priority, status, user_id, due_date, created_at.
9. El status por default es todo. No se acepta en el POST; solo se modifica vía PATCH.
10. Consultar tarea inexistente regresa 404 "tarea no encontrada".
11. El rango de prioridad es de 1 a 5, siendo 1 alta prioridad. Fuera de rango da error 422.
12. Fecha en el pasado (o igual a hoy) debe dar error 422.
13. El título acepta de 1 a 120 caracteres.
14. El campo description es opcional (puede ser null). Si se envía, acepta un máximo de 500 caracteres.
15. DELETE de tarea inexistente regresa 404.
16. PATCH de tarea inexistente regresa 404.
17. Si en un PATCH se cambia el user_id, debe validar que el nuevo usuario exista; si no, regresa 404.
18. Las mismas validaciones del POST aplican en el PATCH para los campos actualizables.
19. PATCH retorna 200 con la tarea actualizada completa.
20. El campo created_at es de tipo datetime, por consistencia con el recurso users.
21. El campo due_date es de tipo date (sin hora).
22. Las operaciones son idempotentes: un PATCH repetido con el mismo cuerpo devuelve 200 con la misma tarea, y un DELETE repetido responde 204 la primera vez y 404 después, sin afectar otras tareas.

Definición de terminado:
Los tests de aceptación en verde. pytest y ruff check en verde. Respeta las convenciones de CLAUDE.md.
Debe tener una cobertura > 80% y branch y mutation testing ejecutado sobre tasks/.

