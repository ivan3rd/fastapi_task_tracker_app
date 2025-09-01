from uuid import UUID

import pytest
from httpx import AsyncClient, ASGITransport

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from app.db import session_manager
from app.main import app
from app.utils import init_admin

from app.settings import APP_ADMIN_PASSWORD, APP_ADMIN_USERNAME, DATABASE_URL, DATABASE_USER

DB_NAME = 'test'
TEST_DB_URL = DATABASE_URL


@pytest.fixture(scope="session")
async def mock_database_url():

    # Создание новой базы данных для тестового окружения
    engine = create_async_engine(
        TEST_DB_URL,
        isolation_level="AUTOCOMMIT"
    )

    async with engine.begin() as conn:
        db_exists = bool((await conn.execute(text(f"SELECT datname FROM pg_catalog.pg_database WHERE datname='{DB_NAME}';"))).scalar())
        if not db_exists:
            await conn.execute(text(f"CREATE DATABASE {DB_NAME} WITH OWNER {DATABASE_USER};"))

    await engine.dispose()
    engine = None
    test_db_url = f"{TEST_DB_URL}{DB_NAME}"
    yield test_db_url

    engine = create_async_engine(
        TEST_DB_URL,
        isolation_level="AUTOCOMMIT"
    )

    # Удаление базы после завершения тестов
    async with engine.begin() as conn:
        await conn.execute(text(f"DROP DATABASE {DB_NAME} WITH (FORCE)"))
    await engine.dispose()


@pytest.fixture(scope="session")
async def db_session(mock_database_url):
    await session_manager.init(mock_database_url)
    await session_manager.connect()
    await session_manager.create_all()
    await init_admin(APP_ADMIN_USERNAME, APP_ADMIN_PASSWORD)
    yield session_manager.session
    await session_manager.session.close()
    await session_manager.close()


@pytest.fixture(scope="session")
async def client():
    client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test/')
    yield client


@pytest.fixture(scope="session")
async def auth_client():
    client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test/')
    auth_data = {'username': APP_ADMIN_USERNAME, 'password': APP_ADMIN_PASSWORD}
    response = await client.post('/login', json=auth_data)
    jwt = response.json()

    client.headers['Authorization'] = f'Bearer {jwt}'
    yield client
