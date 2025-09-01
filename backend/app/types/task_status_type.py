from enum import Enum


class TaskStatusTypeEnum(str, Enum):
    CREATED = 'created'
    IN_PROGRESS = 'in_progress'
    FINISHED = 'finished'

    def __str__(self):
        return str(self.value)

