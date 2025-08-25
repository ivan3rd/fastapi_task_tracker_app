from contextlib import asynccontextmanager
from .session import session_manager


@asynccontextmanager
async def db_session():
    """Provides a database session with automatic cleanup"""
    session = await session_manager.get_session()
    try:
        yield session
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()


@asynccontextmanager
async def db_transaction():
    """Provides a database session with automatic transaction handling"""
    async with db_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
