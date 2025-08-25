from contextvars import ContextVar
from .base import Base
from .transaction import db_session


class SessionConnectionManager():

    def __init__(self):
        self.cbs = ContextVar('db_session')

    async def connect(self):
        async with db_session() as session:
            self.cbs.set(session)

    @property
    def session(self):
        return self.cbs.get('db_session')


db_session_manager = SessionConnectionManager()
