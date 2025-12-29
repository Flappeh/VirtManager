from fastapi import APIRouter

from app.api.routes import items, login, private, users, utils, plugins
from app.core.config import settings

api_router = APIRouter()

def register_core_routes():
    api_router.include_router(login.router)
    api_router.include_router(users.router)
    api_router.include_router(utils.router)
    api_router.include_router(items.router)
    api_router.include_router(plugins.router)
    
if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)

register_core_routes()