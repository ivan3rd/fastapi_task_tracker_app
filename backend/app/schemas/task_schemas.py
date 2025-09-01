from uuid import UUID
from datetime import datetime

from app.types import TaskStatusTypeEnum
from .utils import SchemaBase


class TaskInSchema(SchemaBase):
    name: str
    description: str


class TaskEditSchema(TaskInSchema):
    status: TaskStatusTypeEnum


class TaskOutSchema(TaskInSchema):
    id: UUID
    status: TaskStatusTypeEnum
    created_at: datetime
    updated_at: datetime
