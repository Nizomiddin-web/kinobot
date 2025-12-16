"""
User handlers - Movie lists and genres
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import (
    get_user, get_top_movies, get_new_movies, get_popular_movies,
    get_random_movie, get_all_genres, get_movies_by_genre,
    get_user_favorites, get_user_history, get_user_ratings,
    get_movie_genres
)
from keyboards import movies_list_keyboard, genres_keyboard, movie_keyboard
from locales import t
from utils import format_movie_list, format_duration
from handlers.user.movie import format_movie_info

router = Router()


# ==================== TOP MOVIES ====================

@router.message(Command("top"))
async def cmd_top(message: Message, session: AsyncSession):
    """Handle /top command"""
    user = await get_user(session, message.from_user.id)
    lang = user.language if user else "uz"
    
    movies = await get_top_movies(session, limit=10)
    
    if not movies:
        await message.answer(t("no_movies", lang))
        return
    
    text = t("top_movies", lang) + format_movie_list(movies, lang)
    
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=movies_list_keyboard(movies, lang)
    )


# ==================== NEW MOVIES ====================

@router.message(Command("new"))
async def cmd_new(message: Message, session: AsyncSession):
    """Handle /new command"""
    user = await get_user(session, message.from_user.id)
    lang = user.language if user else "uz"
    
    movies = await get_new_movies(session, limit=10)
    
    if not movies:
        await message.answer(t("no_movies", lang))
        return
    
    text = t("new_movies", lang) + format_movie_list(movies, lang)
    
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=movies_list_keyboard(movies, lang)
    )


# ==================== POPULAR MOVIES ====================

@router.message(Command("popular"))
async def cmd_popular(message: Message, session: AsyncSession):
    """Handle /popular command"""
    user = await get_user(session, message.from_user.id)
    lang = user.language if user else "uz"
    
    movies = await get_popular_movies(session, limit=10)
    
    if not movies:
        await message.answer(t("no_movies", lang))
        return
    
    text = t("popular_movies", lang) + format_movie_list(movies, lang)
    
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=movies_list_keyboard(movies, lang)
    )


# ==================== RANDOM MOVIE ====================

@router.message(Command("random"))
async def cmd_random(message: Message, session: AsyncSession):
    """Handle /random command"""
    user = await get_user(session, message.from_user.id)
    lang = user.language if user else "uz"
    
    movie = await get_random_movie(session)
    
    if not movie:
        await message.answer(t("no_movies", lang))
        return
    
    # Get genres
    genres = await get_movie_genres(session, movie.id)
    
    text = t("random_movie", lang) + "\n\n" + format_movie_info(movie, genres, lang)
    
    from database.crud import is_favorite
    is_fav = await is_favorite(session, message.from_user.id, movie.id)
    
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=movie_keyboard(movie.id, is_fav, lang)
    )


# ==================== GENRES ====================

@router.message(Command("genres"))
async def cmd_genres(message: Message, session: AsyncSession):
    """Handle /genres command"""
    user = await get_user(session, message.from_user.id)
    lang = user.language if user else "uz"
    
    genres = await get_all_genres(session)
    
    if not genres:
        await message.answer(t("no_movies", lang))
        return
    
    await message.answer(
        t("genres_list", lang),
        parse_mode="HTML",
        reply_markup=genres_keyboard(genres, lang)
    )


@router.callback_query(F.data.startswith("genre:"))
async def show_genre_movies(callback: CallbackQuery, session: AsyncSession):
    """Show movies by genre"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"
    
    genre_id = int(callback.data.split(":")[1])
    
    from database.crud import get_genre
    genre = await get_genre(session, genre_id)
    
    if not genre:
        await callback.answer(t("error_occurred", lang), show_alert=True)
        return
    
    movies = await get_movies_by_genre(session, genre_id, limit=20)
    
    if not movies:
        await callback.answer(t("no_movies", lang), show_alert=True)
        return
    
    text = t("genre_movies", lang, genre=genre.get_name(lang))
    text += format_movie_list(movies[:10], lang)
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=movies_list_keyboard(movies[:10], lang)
    )
    await callback.answer()


# ==================== FAVORITES ====================

@router.message(Command("favorites"))
async def cmd_favorites(message: Message, session: AsyncSession):
    """Handle /favorites command"""
    user = await get_user(session, message.from_user.id)
    lang = user.language if user else "uz"
    
    movies = await get_user_favorites(session, message.from_user.id)
    
    if not movies:
        await message.answer(t("favorites_empty", lang))
        return
    
    text = t("favorites_list", lang) + format_movie_list(movies[:20], lang)
    
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=movies_list_keyboard(movies[:10], lang)
    )


# ==================== HISTORY ====================

@router.message(Command("history"))
async def cmd_history(message: Message, session: AsyncSession):
    """Handle /history command"""
    user = await get_user(session, message.from_user.id)
    lang = user.language if user else "uz"
    
    movies = await get_user_history(session, message.from_user.id)
    
    if not movies:
        await message.answer(t("history_empty", lang))
        return
    
    text = t("history_list", lang) + format_movie_list(movies[:20], lang)
    
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=movies_list_keyboard(movies[:10], lang)
    )


# ==================== MY RATINGS ====================

@router.message(Command("my_ratings"))
async def cmd_my_ratings(message: Message, session: AsyncSession):
    """Handle /my_ratings command"""
    user = await get_user(session, message.from_user.id)
    lang = user.language if user else "uz"
    
    ratings = await get_user_ratings(session, message.from_user.id)
    
    if not ratings:
        await message.answer(t("ratings_empty", lang))
        return
    
    text = t("my_ratings", lang)
    
    for movie, rating in ratings[:20]:
        stars = "⭐" * rating
        text += f"• <b>{movie.get_title(lang)}</b> - {stars}\n"
        text += f"  🆔 <code>{movie.id}</code>\n\n"
    
    await message.answer(text, parse_mode="HTML")
