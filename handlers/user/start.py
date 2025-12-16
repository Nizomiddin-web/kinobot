"""
User handlers - Start, Help, Language
"""

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import get_or_create_user, get_user, update_user_language, get_active_channels
from keyboards import language_keyboard, subscription_keyboard, main_menu_keyboard
from locales import t
from utils import check_subscription

router = Router()


async def check_and_request_subscription(
    message: Message,
    bot: Bot,
    session: AsyncSession,
    user_id: int,
    lang: str
) -> bool:
    """
    Check subscription and send request if not subscribed.
    Returns True if subscribed, False if not.
    """
    channels = await get_active_channels(session)

    if not channels:
        return True

    is_subscribed, not_subscribed = await check_subscription(bot, user_id, channels)

    if not is_subscribed:
        await message.answer(
            t("subscribe_required", lang),
            reply_markup=await subscription_keyboard(bot,not_subscribed, lang)
        )
        return False

    return True


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, bot: Bot):
    """Handle /start command"""
    user, is_new = await get_or_create_user(
        session,
        user_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username
    )

    lang = user.language if user else "uz"

    # Check for deep link (movie_123)
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("movie_"):
        movie_id_str = args[1].replace("movie_", "")
        if movie_id_str.isdigit():
            # First check subscription!
            is_subscribed = await check_and_request_subscription(
                message, bot, session, message.from_user.id, lang
            )

            if not is_subscribed:
                # Save movie_id to send after subscription
                from aiogram.fsm.context import FSMContext
                # We'll handle this in check_sub callback
                return

            # User is subscribed, send movie
            from handlers.user.movie import get_movie_by_id
            await get_movie_by_id(message, session, bot, int(movie_id_str))
            return

    if is_new:
        # Show language selection for new users
        await message.answer(
            t("choose_language", "uz"),
            reply_markup=language_keyboard()
        )
    else:
        # Check subscription
        is_subscribed = await check_and_request_subscription(
            message, bot, session, message.from_user.id, lang
        )

        if not is_subscribed:
            return

        # Welcome with main menu
        welcome_text = t("welcome", lang, name=message.from_user.first_name)
        welcome_text += "\n\n" + ("📌 Quyidagi bo'limlardan birini tanlang:" if lang == "uz"
                                  else "📌 Выберите раздел:" if lang == "ru"
                                  else "📌 Select a section:")

        await message.answer(
            welcome_text,
            reply_markup=main_menu_keyboard(lang)
        )


@router.callback_query(F.data.startswith("lang:"))
async def process_language(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    """Handle language selection"""
    lang = callback.data.split(":")[1]

    await update_user_language(session, callback.from_user.id, lang)

    await callback.message.edit_text(t("language_changed", lang))

    # Check subscription after language selection
    is_subscribed = await check_and_request_subscription(
        callback.message, bot, session, callback.from_user.id, lang
    )

    if not is_subscribed:
        await callback.answer()
        return

    # Send welcome message with main menu
    welcome_text = t("welcome", lang, name=callback.from_user.first_name)
    welcome_text += "\n\n" + ("📌 Quyidagi bo'limlardan birini tanlang:" if lang == "uz"
                              else "📌 Выберите раздел:" if lang == "ru"
                              else "📌 Select a section:")

    await callback.message.answer(
        welcome_text,
        reply_markup=main_menu_keyboard(lang)
    )

    await callback.answer()


@router.message(Command("language"))
async def cmd_language(message: Message, session: AsyncSession):
    """Handle /language command"""
    user = await get_user(session, message.from_user.id)
    lang = user.language if user else "uz"

    await message.answer(
        t("choose_language", lang),
        reply_markup=language_keyboard()
    )


@router.message(Command("help"))
async def cmd_help(message: Message, session: AsyncSession):
    """Handle /help command"""
    user = await get_user(session, message.from_user.id)
    lang = user.language if user else "uz"

    bot_info = await message.bot.get_me()

    await message.answer(
        t("help", lang, bot_username=bot_info.username),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "check_sub")
async def process_check_subscription(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    """Handle subscription check"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"

    channels = await get_active_channels(session)

    if not channels:
        await callback.answer(t("subscribed_success", lang), show_alert=True)
        await callback.message.delete()
        return

    is_subscribed, not_subscribed = await check_subscription(
        bot, callback.from_user.id, channels
    )

    if is_subscribed:
        await callback.answer(t("subscribed_success", lang), show_alert=True)
        await callback.message.delete()

        # Send welcome message with main menu
        welcome_text = t("welcome", lang, name=callback.from_user.first_name)
        welcome_text += "\n\n" + ("📌 Quyidagi bo'limlardan birini tanlang:" if lang == "uz"
                                  else "📌 Выберите раздел:" if lang == "ru"
                                  else "📌 Select a section:")

        await callback.message.answer(
            welcome_text,
            reply_markup=main_menu_keyboard(lang)
        )
    else:
        await callback.answer(t("not_subscribed", lang), show_alert=True)

        # Update keyboard with remaining channels
        await callback.message.edit_reply_markup(
            reply_markup=await subscription_keyboard(bot,not_subscribed, lang)
        )