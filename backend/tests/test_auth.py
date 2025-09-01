import pytest
from httpx import AsyncClient, ASGITransport

from app.settings import APP_ADMIN_PASSWORD, APP_ADMIN_USERNAME, DATABASE_URL
from app.main import app


async def test_login(db_session):
    auth_data = {'username': APP_ADMIN_USERNAME, 'password': APP_ADMIN_PASSWORD}
    client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test/')

    response = await client.post('/login', json=auth_data)
    assert response.status_code == 200
    jwt = response.json()

    response = await client.get('/who_am_i')
    assert response.status_code == 401

    headers = {'Authorization': f'Bearer {jwt}', 'accept': 'application/json'}

    response = await client.get('/who_am_i', headers=headers)
    assert response.status_code == 200
