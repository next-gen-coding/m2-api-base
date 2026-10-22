"""Rutas HTTP del recurso `tasks`.

Patrón de referencia para nuevas rutas:
  - un `APIRouter` con `prefix` y `tags`
  - `response_model=` siempre; nunca devolver `dict` crudos
  - la función delega en `service.py` y no contiene lógica de negocio
  - los errores los levanta `service.py` con `core.errors`
"""
from fastapi import APIRouter, Response, status

from tasks import service
from tasks.schemas import Task, TaskCreate, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[Task])
def list_tasks() -> list[Task]:
    return service.list_tasks()


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: int) -> Task:
    return service.get_task(task_id)


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate) -> Task:
    return service.create_task(data)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> Response:
    service.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{task_id}", response_model=Task)
def update_task(task_id: int, data: TaskUpdate) -> Task:
    return service.update_task(task_id, data)
