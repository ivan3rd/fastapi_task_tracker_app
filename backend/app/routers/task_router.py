import logging
from uuid import UUID
from math import ceil

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select, delete

from app.authentication import auth_manager, authenticate_user
from app.schemas import (
    TaskInSchema, TaskEditSchema,
    TaskOutSchema, PaginationResponse
)
from app.models import TaskModel
from app.db import db_session, session_manager
from app.types import TaskStatusTypeEnum


logger = logging.getLogger('uvicorn.error')

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED,)
async def post_task(
    data: TaskInSchema,
    user = Depends(authenticate_user),
    db_session = Depends(session_manager.activate_db_connection),
) -> TaskOutSchema:
    """
    POST /tasks\n
    Создание новой задачи. Статус новой задачи всегда будет = 'created';\n
    name - название задачи; description - описание задачи.\n
    """
    task = TaskModel(
        name=data.name,
        description=data.description,
    )
    session_manager.session.add(task)
    await session_manager.session.flush()

    return TaskOutSchema.model_validate(task)


@router.get("")
async def get_list_tasks(
    page: int = 1,
    page_size: int = 100,
    task_status: TaskStatusTypeEnum | None = None,
    user = Depends(authenticate_user),
    db_session = Depends(session_manager.activate_db_connection),
) -> PaginationResponse:
    """
    GET /tasks\n
    Получение пагинированного списка задач.\n
    Есть возможность фильтрации по статусам task_status.\n
    """

    logger.info('TASK_ROUTER')
    logger.info(session_manager.db_session_context)
    tasks = await TaskModel.get_butch(
        page=page, page_size=page_size, task_status=task_status
    )
    tasks_total = await TaskModel.get_total_count(task_status=task_status)
    total_pages = ceil(tasks_total/page_size)

    return PaginationResponse(
        current_page=page,
        page_size=page_size,
        total_pages=total_pages,
        total_items=tasks_total,
        results=[TaskOutSchema.model_validate(_) for _ in tasks]
    )


@router.get("/{task_id}")
async def get_task(
    task_id: UUID,
    user = Depends(authenticate_user),
    db_session = Depends(session_manager.activate_db_connection),
) -> TaskOutSchema:
    """
    GET /tasks/{task_id}\n
    Вывод одной задачи по приведённому task_id.\n
    name - название задачи; description - описание задачи.\n
    """

    task = await TaskModel.get_task(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Задача не была найдена',
        )

    return TaskOutSchema.model_validate(task)


@router.put("/{task_id}")
async def edit_task(
    task_id: UUID,
    data: TaskEditSchema,
    user = Depends(authenticate_user),
    db_session = Depends(session_manager.activate_db_connection),
) -> TaskOutSchema:
    """
    PUT /tasks/{task_id}\n
    Редактирование задачи, в том числе и её статуса.\n
    name - название задачи; description - описание задачи; status - статус задачи\n
    status задачи может быть 'created', 'in_progress', 'finished'\n
    """

    task = await TaskModel.get_task(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Задача не была найдена',
    )

    for key in data.__fields__.keys():
        setattr(task, key, getattr(data, key))

    return TaskOutSchema.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    user = Depends(authenticate_user),
    db_session = Depends(session_manager.activate_db_connection),
):
    """
    DELETE /tasks/{task_id}\n
    Удаление одной из задач по приведённому id.\n
    """

    task = await TaskModel.get_task(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Задача не была найдена',
        )

    await session_manager.session.execute(
        delete(TaskModel)
        .where(TaskModel.id == task_id)
    )
