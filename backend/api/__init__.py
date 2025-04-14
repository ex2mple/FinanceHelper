from fastapi import APIRouter

from .users.views import router as users_router
from .auth.views import router as auth_router
from .categories.views import router as category_router
from .transactions.views import router as transaction_router
from .ai.views import router as ai_router

router = APIRouter()
router.include_router(users_router, prefix='/users')
router.include_router(auth_router, prefix='/auth')
router.include_router(category_router, prefix='/categories')
router.include_router(transaction_router, prefix='/transactions')
router.include_router(ai_router, prefix='/ai')
