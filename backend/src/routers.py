from fastapi import APIRouter

from src.auth.api import router as auth_router
from src.items.api import router as item_router
from src.users.api import router as user_router

api_router = APIRouter()

api_router.include_router(auth_router, tags=['login'])
api_router.include_router(user_router, prefix='/users', tags=['users'])
api_router.include_router(item_router, prefix='/items', tags=['items'])
