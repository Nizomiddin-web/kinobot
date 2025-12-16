"""
User handlers - Movie operations
"""

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import (
    get_user, get_or_create_user, get_movie, increment_movie_views, add_to_history,
    get_movie_genres, is_favorite, add_favorite, remove_favorite,
    add_rating, get_user_rating
)
from handlers.user.start import check_and_request_subscription
from keyboards import movie_keyboard, rating_keyboard, main_menu_keyboard
from locales import t
from utils import extract_movie_id, format_duration

router = Router()


def format_movie_info(movie, genres: list, lang: str = "uz") -> str:
    """Format movie info text"""
    genre_names = ", ".join([g.get_name(lang) for g in genres]) if genres else "—"

    return t(
        "movie_info", lang,
        title=movie.get_title(lang),
        year=movie.year,
        language=movie.language,
        quality=movie.quality,
        genres=genre_names,
        category=movie.category,
        duration=format_duration(movie.duration),
        rating=f"{movie.user_rating:.1f}" if movie.rating_count > 0 else "—",
        count=movie.rating_count,
        views=movie.views,
        id=movie.id
    )


async def get_movie_by_id(message: Message, session: AsyncSession, bot: Bot, movie_id: int):
    """Get movie by ID - used for deep links"""
    # Get or create user first
    user, _ = await get_or_create_user(
        session,
        user_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username
    )
    lang = user.language if user else "uz"

    movie = await get_movie(session, movie_id)

    if not movie:
        await message.answer(t("movie_not_found", lang))
        return

    # Get genres
    genres = await get_movie_genres(session, movie.id)

    # Check if favorite
    is_fav = await is_favorite(session, message.from_user.id, movie.id)

    # Increment views
    await increment_movie_views(session, movie.id)

    # Add to history
    # await add_to_history(session, message.from_user.id, movie.id)

    # Send movie info
    info_text = format_movie_info(movie, genres, lang)

    if movie.is_series:
        await message.answer(info_text,reply_markup=movie_keyboard(movie.id, is_fav, lang,True,movie.total_episodes))
    else:
        try:
            await message.answer_video(
                    video=movie.file_id,
                    caption=info_text,
                    reply_markup=movie_keyboard(movie.id, is_fav, lang),
                    parse_mode="HTML"
                )
        except:
            await message.answer(t("error_occurred", lang))


@router.message(F.text.regexp(r'^\d+$'))
async def get_movie_by_code(message: Message, session: AsyncSession, bot: Bot):
    """Handle movie code input"""
    # Get or create user first
    user, _ = await get_or_create_user(
        session,
        user_id=message.from_user.id,
        full_name=message.from_user.full_name,
        username=message.from_user.username
    )
    lang = user.language if user else "uz"
    # First check subscription!
    is_subscribed = await check_and_request_subscription(
        message, bot, session, message.from_user.id, lang
    )

    if not is_subscribed:
        # Save movie_id to send after subscription
        from aiogram.fsm.context import FSMContext
        # We'll handle this in check_sub callback
        return
    movie_id = extract_movie_id(message.text)

    if not movie_id:
        return

    movie = await get_movie(session, movie_id)

    if not movie:
        await message.answer(t("movie_not_found", lang))
        return

    # Get genres
    genres = await get_movie_genres(session, movie.id)

    # Check if favorite
    is_fav = await is_favorite(session, message.from_user.id, movie.id)

    # Increment views
    await increment_movie_views(session, movie.id)

    # Add to history
    # await add_to_history(session, message.from_user.id, movie.id)

    # Send movie info
    info_text = format_movie_info(movie, genres, lang)

    # try:
    if movie.is_series:
        await message.answer(info_text,reply_markup=movie_keyboard(movie.id, is_fav, lang,True,movie.total_episodes))
    else:
        try:
             await message.answer_video(
                video=movie.file_id,
                caption=info_text,
                reply_markup=movie_keyboard(movie.id, is_fav, lang)
            )
        except:
            await message.answer(t("error_occurred", lang))


@router.callback_query(F.data.startswith("back"))
async def back_main(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    user, _ = await get_or_create_user(
        session,
        user_id=callback.from_user.id,
        full_name=callback.from_user.full_name,
        username=callback.from_user.username
    )
    lang = user.language if user else "uz"
    await callback.message.edit_text(
        'Bosh menu',
        reply_markup=main_menu_keyboard(lang)
    )

@router.callback_query(F.data.startswith("movie:"))
async def show_movie(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    """Show movie by callback"""
    # Get or create user first
    user, _ = await get_or_create_user(
        session,
        user_id=callback.from_user.id,
        full_name=callback.from_user.full_name,
        username=callback.from_user.username
    )
    lang = user.language if user else "uz"

    movie_id = int(callback.data.split(":")[1])
    movie = await get_movie(session, movie_id)

    if not movie:
        await callback.answer(t("movie_not_found", lang), show_alert=True)
        return

    # Get genres
    genres = await get_movie_genres(session, movie.id)

    # Check if favorite
    is_fav = await is_favorite(session, callback.from_user.id, movie.id)

    # Increment views
    await increment_movie_views(session, movie.id)

    # Add to history
    # await add_to_history(session, callback.from_user.id, movie.id)

    # Send movie info
    info_text = format_movie_info(movie, genres, lang)

    # Send video
    try:
            await callback.message.answer_video(
                video=movie.file_id,
                caption=info_text,
                reply_markup=movie_keyboard(movie.id, is_fav, lang),
                parse_mode="HTML"
            )
    except:
            await callback.answer(t("error_occurred", lang), show_alert=True)

    await callback.answer()


@router.callback_query(F.data.startswith("get:"))
async def get_movie_inline(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    """Get movie from inline result"""
    await show_movie(callback, session, bot)


# ==================== RATING ====================

@router.callback_query(F.data.startswith("rate:"))
async def show_rating_keyboard(callback: CallbackQuery, session: AsyncSession):
    """Show rating keyboard"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"

    movie_id = int(callback.data.split(":")[1])

    # Check existing rating
    existing = await get_user_rating(session, callback.from_user.id, movie_id)

    text = t("rate_movie", lang)
    if existing:
        text += f"\n\nSizning bahoyingiz: {'⭐' * existing.rating}"

    await callback.message.edit_reply_markup(
        reply_markup=rating_keyboard(movie_id, lang)
    )
    await callback.answer(text)


@router.callback_query(F.data.startswith("setrate:"))
async def set_rating(callback: CallbackQuery, session: AsyncSession):
    """Set movie rating"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"

    parts = callback.data.split(":")
    movie_id = int(parts[1])
    rating = int(parts[2])

    # Save rating
    is_new, new_avg = await add_rating(session, callback.from_user.id, movie_id, rating)

    await callback.answer(
        t("rating_saved", lang, rating=new_avg),
        show_alert=True
    )

    # Update keyboard
    is_fav = await is_favorite(session, callback.from_user.id, movie_id)
    await callback.message.edit_reply_markup(
        reply_markup=movie_keyboard(movie_id, is_fav, lang)
    )


# ==================== FAVORITES ====================

@router.callback_query(F.data.startswith("fav:"))
async def add_to_favorites(callback: CallbackQuery, session: AsyncSession):
    """Add movie to favorites"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"

    movie_id = int(callback.data.split(":")[1])

    added = await add_favorite(session, callback.from_user.id, movie_id)

    if added:
        await callback.answer(t("added_to_favorites", lang), show_alert=True)

        # Update keyboard
        await callback.message.edit_reply_markup(
            reply_markup=movie_keyboard(movie_id, True, lang)
        )
    else:
        await callback.answer(t("already_in_favorites", lang), show_alert=True)


@router.callback_query(F.data.startswith("unfav:"))
async def remove_from_favorites(callback: CallbackQuery, session: AsyncSession):
    """Remove movie from favorites"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"

    movie_id = int(callback.data.split(":")[1])

    removed = await remove_favorite(session, callback.from_user.id, movie_id)

    if removed:
        await callback.answer(t("removed_from_favorites", lang), show_alert=True)

        # Update keyboard
        await callback.message.edit_reply_markup(
            reply_markup=movie_keyboard(movie_id, False, lang)
        )


@router.callback_query(F.data == "noop")
async def noop_callback(callback: CallbackQuery):
    """Do nothing callback for pagination display"""
    await callback.answer()