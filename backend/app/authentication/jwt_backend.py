import logging
from uuid import UUID
from jose import JWTError, jwt
from fastapi import Request
from starlette.authentication import (
    AuthenticationBackend, AuthenticationError, SimpleUser, AuthCredentials
)

from app.models import UserModel


logger = logging.getLogger('uvicorn.error')


class JWTUser(SimpleUser):
    def __init__(self, username: str,  id: UUID, admin: bool = False,):
        logger.info('JWTUser')
        super().__init__(username)
        self.admin = admin
        self.id = id

    @property
    def is_authenticated(self) -> bool:
        return True

class JWTAuthenticationBackend(AuthenticationBackend):

    def __init__(self, secret: str, algorithm: str):
        logger.info('JWTAuthenticationBackend.__init__')
        self.secret = secret
        self.algorithm = algorithm


    async def authenticate(self, request: Request):
        logger.info('JWTAuthenticationBackend.authenticate')
        if "Authorization" not in request.headers:
            return None

        auth_header = request.headers["Authorization"]
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                return None

            # Decode JWT token
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            logger.info('payload')
            logger.info(payload)
            username = payload.get("username")
            is_admin = payload.get("admin", False)
            _id = payload.get("id", False)

            if username and UserModel.get_by_username(username):
                return AuthCredentials([]), JWTUser(username, _id, is_admin)

        except (ValueError, JWTError):
            pass

        raise AuthenticationError("Invalid token")

