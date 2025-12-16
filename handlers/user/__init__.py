"""
User handlers package
"""

from aiogram import Router

from .start import router as start_router
from .movie import router as movie_router
from .search import router as search_router
from .lists import router as lists_router
from .menu import router as menu_router
from .episode import router as episodes_router


def get_user_router() -> Router:
    """Get combined user router"""
    router = Router()

    router.include_router(start_router)
    router.include_router(menu_router)
    router.include_router(episodes_router)
    router.include_router(search_router)
    router.include_router(lists_router)
    router.include_router(movie_router)  # Should be last (catches digit messages)
     # Should be last (catches digit messages)

    return router