"""
Kino Bot - Main entry point
Telegram bot for movie sharing with subscription checking

Features:
- Movie management (add via caption/inline/minimal)
- Multi-language support (uz/ru/en)
- User ratings and favorites
- Watch history
- Forced subscription
- Inline search
- Admin panel
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import config, DEFAULT_GENRES
from database import init_db, async_session, Base, engine
from database.models import Genre, Admin
from database.crud import get_genre_by_name, create_genre, add_admin, is_admin
from handlers import get_all_routers
from middlewares import DatabaseMiddleware, SubscriptionMiddleware, BannedUserMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def setup_database():
    """Initialize database and create default data"""
    logger.info("Initializing database...")
    
    # Create tables
    await init_db()
    
    # Add default genres
    async with async_session() as session:
        for genre_data in DEFAULT_GENRES:
            existing = await get_genre_by_name(session, genre_data["name"])
            if not existing:
                await create_genre(
                    session,
                    name=genre_data["name"],
                    name_uz=genre_data["name_uz"],
                    name_ru=genre_data["name_ru"],
                    name_en=genre_data["name_en"]
                )
                logger.info(f"Created genre: {genre_data['name']}")
        
        # Add super admins from config
        for admin_id in config.SUPER_ADMIN_IDS:
            if not await is_admin(session, admin_id):
                await add_admin(session, admin_id, role="superadmin")
                logger.info(f"Added superadmin: {admin_id}")
    
    logger.info("Database initialized successfully")


async def on_startup(bot: Bot):
    """Startup handler"""
    logger.info("Bot is starting...")
    
    # Setup database
    await setup_database()
    
    # Get bot info
    bot_info = await bot.get_me()
    logger.info(f"Bot started: @{bot_info.username}")
    
    # Notify admins
    for admin_id in config.SUPER_ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"🤖 Bot ishga tushdi!\n\n"
                f"Bot: @{bot_info.username}\n"
                f"Database: {config.DATABASE_TYPE}"
            )
        except Exception as e:
            logger.warning(f"Failed to notify admin {admin_id}: {e}")


async def on_shutdown(bot: Bot):
    """Shutdown handler"""
    logger.info("Bot is shutting down...")
    
    # Notify admins
    for admin_id in config.SUPER_ADMIN_IDS:
        try:
            await bot.send_message(admin_id, "🔴 Bot to'xtatildi!")
        except:
            pass


async def main():
    """Main function"""
    # Check config
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN is not set!")
        return
    
    # Create bot
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Create dispatcher
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register middlewares
    dp.message.middleware(DatabaseMiddleware(async_session))
    dp.callback_query.middleware(DatabaseMiddleware(async_session))
    dp.inline_query.middleware(DatabaseMiddleware(async_session))
    dp.channel_post.middleware(DatabaseMiddleware(async_session))
    
    dp.message.middleware(BannedUserMiddleware())
    dp.callback_query.middleware(BannedUserMiddleware())
    
    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())
    
    # Register routers
    dp.include_router(get_all_routers())
    
    # Register startup/shutdown handlers
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Start polling
    logger.info("Starting bot polling...")
    
    try:
        await dp.start_polling(
            bot,
            allowed_updates=[
                "message",

                "callback_query",
                "inline_query",
                "channel_post"
            ]
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        raise
