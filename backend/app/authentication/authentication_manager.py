import logging
from datetime import timedelta, datetime
from jose import jwt
from fastapi import HTTPException, status

from app.models import UserModel
from app.settings import JWT_SECRET_KEY, JWT_ALGORITHM
from app.schemas import AuthSchema

logger = logging.getLogger('uvicorn.error')


class AuthenticationManager():

    def __init__(
        self,
        access_token_expires=30,
    ):
        self.secret = JWT_SECRET_KEY
        self.algorithm = JWT_ALGORITHM
        self.access_token_expires = timedelta(minutes=access_token_expires)

    def create_access_token(self, data: dict, expires_delta: timedelta = timedelta(minutes=15)):
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=self.algorithm)

    async def authenticate_user(self, data: AuthSchema):
        user = await UserModel.get_by_username(username=data.username)
        if not user.check_password(password=data.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Не правильно набраны логин или пароль",
                                headers={"WWW-Authenticate": "Bearer"},
                                )
        return user


auth_manager = AuthenticationManager()
