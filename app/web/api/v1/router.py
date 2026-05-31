from fastapi import APIRouter

from app.settings import Tags
from app.web.api.v1.auth import router as auth_router
from app.web.api.v1.users import router as users_router

router = APIRouter()
router.include_router(users_router, prefix="/users", tags=[Tags.USERS])
router.include_router(auth_router, prefix="/auth", tags=[Tags.AUTH])
