from core.fastapi_util import AppRouter

router = AppRouter()

@router.post("/login")
async def login():
    return {"message": "Login successful"}
