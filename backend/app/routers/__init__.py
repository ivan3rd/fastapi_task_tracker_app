from fastapi import APIRouter

from .auth_router import router as auth_router
from .task_router import router as task_router


main_router = APIRouter()
main_router.include_router(auth_router, prefix="")
main_router.include_router(task_router, prefix="/tasks")
