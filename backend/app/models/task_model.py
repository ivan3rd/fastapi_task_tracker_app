from __future__ import annotations
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from app.types import TaskStatusTypeEnum
from app.db import Base, session_manager


class TaskModel(Base):
    __tablename__ = 'task'

    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow, server_default=sa.func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, server_default=sa.func.now(), server_onupdate=sa.func.now(), nullable=False)

    name = sa.Column(sa.String(), nullable=False)
    description = sa.Column(sa.String(), default='', nullable=False)

    status = sa.Column(
        sa.Enum(*[x.value for x in TaskStatusTypeEnum], name='task_status_type'),
        nullable=False,
        default=TaskStatusTypeEnum.CREATED,
    )

    @classmethod
    async def get_task(cls, task_id: UUID) -> TaskModel | None:
        task = (await session_manager.session.scalars(
            sa.select(TaskModel)
            .where(TaskModel.id == task_id)
        )).one_or_none()

        return task

    @classmethod
    async def get_total_count(
        cls,
        task_status: TaskStatusTypeEnum | None = None,
    ) -> int:
        query = sa.select(sa.func.count(TaskModel.id))
        if task_status:
            query = query.where(TaskModel.status == task_status)
        return (await session_manager.session.scalar(query))

    @classmethod
    async def get_butch(
        cls, page: int | None = None,
        page_size: int | None = None,
        task_status: TaskStatusTypeEnum | None = None,
    ) -> list[TaskModel]:
        query = sa.select(TaskModel)
        if task_status:
            query = query.where(TaskModel.status == task_status)
        if page and page_size:
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)
        return (await session_manager.session.scalars(query)).all()

