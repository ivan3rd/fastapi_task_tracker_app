import logging
from sqlalchemy import select
from app.models import UserModel
from app.db import db_session

logger = logging.getLogger('uvicorn.error')


async def init_admin(username: str, password: str):
    logger.info(f'init_admin. Ищем пользователя с username={username}')
    admin = await UserModel.get_by_username(username)
    if admin:
        if admin.password != password:
            raise Exception('Не верный пароль для админа. Измените в .env логин или пароль')
        if admin.admin is False:
            raise Exception('Этот пользователь уже существует, но не имеет прав админа. Измените в .env логин или пароль')
        return
    logger.info(f'init_admin. Пользователь {username} не найден. Создаём нового админа')

    admin = UserModel(
        username = username,
        password = password,
        admin = True,
    )

    async with db_session() as session:
        session.add(admin)
        await session.commit()
