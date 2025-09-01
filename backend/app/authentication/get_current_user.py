from fastapi import Request, HTTPException, status
from .jwt_backend import JWTUser


def authenticate_user(request: Request) -> JWTUser:
    if not request.user.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return request.user

