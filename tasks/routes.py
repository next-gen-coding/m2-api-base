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
    return service.create_task(data)
