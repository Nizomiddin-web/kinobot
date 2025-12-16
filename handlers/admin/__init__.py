"""
Admin handlers package
"""

from aiogram import Router

from .panel import router as panel_router
from .movie import router as movie_router
from .channel import router as channel_router
from .broadcast import router as broadcast_router
from .episode import router as episode_router

def get_admin_router() -> Router:
    """Get combined admin router"""
    router = Router()
    
    router.include_router(panel_router)
    router.include_router(movie_router)
    router.include_router(episode_router)
    router.include_router(channel_router)
    router.include_router(broadcast_router)
    
    return router
