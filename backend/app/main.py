from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from starlette.middleware.authentication import AuthenticationMiddleware

from app.db import session_manager
from app.utils import init_admin
from app.authentication import JWTAuthenticationBackend
from app.settings import ( DATABASE_URL_FULL, APP_ADMIN_USERNAME, APP_ADMIN_PASSWORD,
    JWT_SECRET_KEY, JWT_ALGORITHM,
)
from app.routers import main_router


import logging
logger = logging.getLogger('uvicorn.error')


@asynccontextmanager
async def lifespan(app: FastAPI):
    await session_manager.init(DATABASE_URL_FULL)
    logger.info('SESSION_MANAGER')
    logger.info('before')
    logger.info(session_manager.db_session_context)
    await session_manager.connect()
    logger.info('after')
    logger.info(session_manager.db_session_context)
    await init_admin(APP_ADMIN_USERNAME, APP_ADMIN_PASSWORD)
    yield
    await session_manager.session.close()
    await session_manager.close()


app = FastAPI(
    lifespan=lifespan,
)

# middleware
app.add_middleware(
    AuthenticationMiddleware,
    backend=JWTAuthenticationBackend(JWT_SECRET_KEY, JWT_ALGORITHM)
)


# routers
app.include_router(main_router, prefix="")


#openapi
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "JWT": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Введите JWT токен: ",
        }
    }

    # Add security to protected paths
    protected_paths = ['/who_am_i', '/tasks']
    for path in openapi_schema["paths"]:
        if any(p in path for p in protected_paths):
            for method in openapi_schema["paths"][path]:
                if "security" not in openapi_schema["paths"][path][method]:
                    openapi_schema["paths"][path][method]["security"] = []
                openapi_schema["paths"][path][method]["security"].append({"JWT": []})


    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
