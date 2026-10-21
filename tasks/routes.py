"""Rutas HTTP del recurso `tasks`.

Siguen el patrón de `users/routes.py`: la función delega en `service.py` y no
contiene lógica de negocio; los errores los levanta `service.py` con `core.errors`.
"""
from fastapi import APIRouter, status

from tasks import service
from tasks.schemas import Task, TaskCreate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate) -> Task:
    """Crea una tarea (`POST /tasks`) delegando en `service.create_task`.

    Args:
        data: Cuerpo JSON de la petición. FastAPI lo valida contra `TaskCreate`
            (título de 1 a 120 caracteres, prioridad `low`/`medium`/`high`).

    Returns:
        La `Task` creada, con código HTTP 201.

    Raises:
        HTTPException: 422 si el cuerpo no cumple el schema, o si `due_date` es
            una fecha pasada (error de dominio levantado en `service.py`).
    """
    return service.create_task(data)
