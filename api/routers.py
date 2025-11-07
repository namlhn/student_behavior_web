from core.fastapi_util import AppRouter
from . import auth_api
from . import students_api

router_api = AppRouter()

router_api.include_router(auth_api.router, prefix="/auth", tags=["Auth API"])
router_api.include_router(students_api.router, tags=["Students API"])