from fastapi import Request, HTTPException, status
from .jwt_backend import JWTUser


def get_current_user(request: Request) -> JWTUser:
    if not request.user.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return request.user


def require_scope(scope: str):
    def dependency(request: Request):
        user = get_current_user(request)
        if not user.has_scope(scope):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required scope: {scope}",
            )
        return user
    return dependency

