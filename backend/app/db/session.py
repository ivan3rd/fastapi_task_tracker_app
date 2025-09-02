import logging
from contextvars import ContextVar
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from .base import Base

logger = logging.getLogger('uvicorn.error')
db_session_context = ContextVar('db_session')

class DatabaseSessionManager:
    def __init__(self):
        self._engine = None
        self._sessionmaker = None
        self.db_session_context = ContextVar('db_session')

    async def init(self, url: str):
        self._engine = create_async_engine(
            url,
            poolclass=NullPool,
            echo=True,
            isolation_level="AUTOCOMMIT",
        )
        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            class_=AsyncSession,
            future=True,
        )

    async def connect(self):
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")
        async with self._sessionmaker() as session:
            self.db_session_context.set(session)

    @property
    def session(self) -> AsyncSession:
        return self.db_session_context.get('db_session')

    async def close(self):
        if self._engine is None:
            return
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    async def get_session(self) -> AsyncSession:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")
        return self._sessionmaker()

    async def create_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_all(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def activate_db_connection(self):
        await self.connect()
        try:
            yield self.session
        except Exception as e:
            logger.error(f'Exception accured, while processing: {e}')
            self.session.rollback()
            raise
        finally:
            await self.session.close()


session_manager = DatabaseSessionManager()
