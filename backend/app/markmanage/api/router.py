from fastapi import APIRouter

from backend.app.markmanage.api.v1.user import router as user_router
from backend.app.markmanage.api.v1.exam import router as exam_router

v1 = APIRouter()

v1.include_router(user_router, prefix='/user', tags=['用户'])
v1.include_router(exam_router, prefix='/exam', tags=['考试'])
