"""
Subscription check middleware
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import get_active_channels, get_user, is_admin
from utils import check_subscription
from keyboards import subscription_keyboard
from locales import t


class SubscriptionMiddleware(BaseMiddleware):
    """Middleware to check user subscription to required channels"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Get session
        session: AsyncSession = data.get("session")
        if not session:
            return await handler(event, data)
        
        # Get user
        if isinstance(event, Message):
            user_id = event.from_user.id
            user = await get_user(session, user_id)
            lang = user.language if user else "uz"
        else:
            user_id = event.from_user.id
            user = await get_user(session, user_id)
            lang = user.language if user else "uz"
        
        # Skip for admins
        if await is_admin(session, user_id):
            return await handler(event, data)
        
        # Skip for check_sub callback
        if isinstance(event, CallbackQuery) and event.data == "check_sub":
            return await handler(event, data)
        
        # Skip for /start command
        if isinstance(event, Message) and event.text and event.text.startswith('/start'):
            return await handler(event, data)
        
        # Get active channels
        channels = await get_active_channels(session)
        
        if not channels:
            return await handler(event, data)
        
        # Check subscription
        bot = data.get("bot")
        is_subscribed, not_subscribed = await check_subscription(bot, user_id, channels)
        
        if is_subscribed:
            return await handler(event, data)
        
        # User is not subscribed - show subscription keyboard
        text = t("subscribe_required", lang)
        keyboard = await subscription_keyboard(bot,not_subscribed, lang)
        
        if isinstance(event, Message):
            await event.answer(text, reply_markup=keyboard)
        else:
            await event.answer(t("not_subscribed", lang), show_alert=True)
            await event.message.answer(text, reply_markup=keyboard)
        
        return None


class DatabaseMiddleware(BaseMiddleware):
    """Middleware to inject database session"""
    
    def __init__(self, session_factory):
        self.session_factory = session_factory
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        async with self.session_factory() as session:
            data["session"] = session
            return await handler(event, data)


class BannedUserMiddleware(BaseMiddleware):
    """Middleware to check if user is banned"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        session: AsyncSession = data.get("session")
        if not session:
            return await handler(event, data)
        
        user_id = event.from_user.id
        user = await get_user(session, user_id)
        
        if user and user.is_banned:
            if isinstance(event, Message):
                await event.answer(t("user_banned", user.language))
            else:
                await event.answer(t("user_banned", "uz"), show_alert=True)
            return None
        
        return await handler(event, data)
