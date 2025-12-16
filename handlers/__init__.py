"""
Handlers package
"""

from aiogram import Router

from .user import get_user_router
from .admin import get_admin_router
from .inline import router as inline_router


def get_all_routers() -> Router:
    """Get all routers combined"""
    router = Router()
    
    # Admin router first (higher priority)
    router.include_router(get_admin_router())
    
    # User router
    router.include_router(get_user_router())
    
    # Inline router
    router.include_router(inline_router)
    
    return router
