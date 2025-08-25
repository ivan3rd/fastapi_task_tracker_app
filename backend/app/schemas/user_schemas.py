from uuid import UUID
from .utils import SchemaBase


class UserSchema(SchemaBase):
    id: UUID | str
    username: str
    admin: bool

