from core.fastapi_util import AppRouter
from . import auth_api

router_api = AppRouter()

router_api.include_router(auth_api.router, prefix="/auth", tags=["Auth API"])