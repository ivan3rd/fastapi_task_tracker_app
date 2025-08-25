from .utils import SchemaBase


class AuthSchema(SchemaBase):
    username: str
    password: str

