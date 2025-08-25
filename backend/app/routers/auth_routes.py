import logging

from fastapi import APIRouter, Request

from app.authentication import auth_manager
from app.schemas import AuthSchema, UserSchema


logger = logging.getLogger('uvicorn.error')


router = APIRouter()


@router.post("/login")
async def post_login(request: Request, data: AuthSchema) -> str:
    """
    POST method\n
    введите логин и пароль, чтобы получить access token\n
    access token можно ввести c помощью кнопки authtorize
    """
    user = await auth_manager.authenticate_user(data)

    access_token = auth_manager.create_access_token(
        {'id': str(user.id), 'username': user.username, 'admin': user.admin},
        expires_delta=auth_manager.access_token_expires
    )
    return access_token


@router.get("/who_am_i")
async def get_user(request: Request) -> UserSchema:
    """
    GET Method \n
    Получение данных о текущем аутентифициорованном пользователе.\n
    Возвращает данные сохранённые в токене\n
    """
    user = request.user

    return UserSchema(
        id=user.id,
        username=user.username,
        admin=user.admin,
    )

