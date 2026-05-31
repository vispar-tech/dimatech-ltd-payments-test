from fastapi.routing import APIRouter

from app.web.api import docs, v1

api_router = APIRouter()
api_router.include_router(docs.router)
api_router.include_router(v1.router, prefix="/v1")
