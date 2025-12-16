"""
User handlers - Menu callbacks
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import (
    get_user, get_top_movies, get_new_movies, get_popular_movies,
    get_random_movie, get_user_favorites, get_user_history,
    get_movies_by_category, get_all_genres, get_movie_genres
)
from keyboards import (
    main_menu_keyboard, settings_keyboard, category_movies_keyboard,
    genres_keyboard, movies_list_keyboard, language_keyboard,
    movie_keyboard, back_keyboard
)
from locales import t
from utils import format_movie_list, format_duration
from config import config

router = Router()


# ==================== MAIN MENU ====================

@router.callback_query(F.data == "menu:main")
async def show_main_menu(callback: CallbackQuery, session: AsyncSession):
    """Show main menu"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"

    text = ("📌 Quyidagi bo'limlardan birini tanlang:" if lang == "uz"
            else "📌 Выберите раздел:" if lang == "ru"
    else "📌 Select a section:")

    await callback.message.edit_text(
        text,
        reply_markup=main_menu_keyboard(lang)
    )
    await callback.answer()


# ==================== CATEGORIES ====================

@router.callback_query(F.data.startswith("cat:"))
async def show_category(callback: CallbackQuery, session: AsyncSession):
    """Show movies by category"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"

    category = callback.data.split(":")[1]

    movies = await get_movies_by_category(session, category, limit=10)

    if not movies:
        await callback.answer(t("no_movies", lang), show_alert=True)
        return

    # Category names
    cat_names = {
        "Kino": {"uz": "🎬 Kinolar", "ru": "🎬 Фильмы", "en": "🎬 Movies"},
        "Serial": {"uz": "📺 Seriallar", "ru": "📺 Сериалы", "en": "📺 Series"},
        "Anime": {"uz": "🎌 Anime", "ru": "🎌 Аниме", "en": "🎌 Anime"},
        "Multfilm": {"uz": "🧸 Multfilmlar", "ru": "🧸 Мультфильмы", "en": "🧸 Cartoons"}
    }

    cat_name = cat_names.get(category, {}).get(lang, category)

    text = f"<b>{cat_name}</b>\n\n"
    text += "Kinoni tanlang:" if lang == "uz" else "Выберите фильм:" if lang == "ru" else "Select a movie:"

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=category_movies_keyboard(movies, category, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("catpage:"))
async def category_pagination(callback: CallbackQuery, session: AsyncSession):
    """Handle category pagination"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"

    parts = callback.data.split(":")
    category = parts[1]
    page = int(parts[2])

    if page < 1:
        page = 1

    offset = (page - 1) * 10
    movies = await get_movies_by_category(session, category, limit=10, offset=offset)

    if not movies:
        await callback.answer(
            "Boshqa kino yo'q" if lang == "uz" else "Больше нет" if lang == "ru" else "No more movies", show_alert=True)
        return

    # Category names
    cat_names = {
        "Kino": {"uz": "🎬 Kinolar", "ru": "🎬 Фильмы", "en": "🎬 Movies"},
        "Serial": {"uz": "📺 Seriallar", "ru": "📺 Сериалы", "en": "📺 Series"},
        "Anime": {"uz": "🎌 Anime", "ru": "🎌 Аниме", "en": "🎌 Anime"},
        "Multfilm": {"uz": "🧸 Multfilmlar", "ru": "🧸 Мультфильмы", "en": "🧸 Cartoons"}
    }

    cat_name = cat_names.get(category, {}).get(lang, category)

    text = f"<b>{cat_name}</b>\n\n"
    text += "Kinoni tanlang:" if lang == "uz" else "Выберите фильм:" if lang == "ru" else "Select a movie:"

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=category_movies_keyboard(movies, category, lang, page)
    )
    await callback.answer()


# ==================== TOP / NEW ====================

@router.callback_query(F.data == "menu:top")
async def show_top_movies(callback: CallbackQuery, session: AsyncSession):
    """Show top rated movies"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"

    movies = await get_top_movies(session, limit=10)

    if not movies:
        await callback.answer(t("no_movies", lang), show_alert=True)
        return

    text = t("top_movies", lang) + format_movie_list(movies, lang)

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=movies_list_keyboard(movies, lang)
    )
    await callback.answer()


@router.callback_query(F.data == "menu:new")
async def show_new_movies(callback: CallbackQuery, session: AsyncSession):
    """Show new movies"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"

    movies = await get_new_movies(session, limit=10)

    if not movies:
        await callback.answer(t("no_movies", lang), show_alert=True)
        return

    text = t("new_movies", lang) + format_movie_list(movies, lang)

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=movies_list_keyboard(movies, lang)
    )
    await callback.answer()


# ==================== FAVORITES / HISTORY ====================

@router.callback_query(F.data == "menu:favorites")
async def show_favorites(callback: CallbackQuery, session: AsyncSession):
    """Show user favorites"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"

    movies = await get_user_favorites(session, callback.from_user.id)

    if not movies:
        text = t("favorites_empty", lang)
        await callback.message.edit_text(
            text,
            reply_markup=back_keyboard("menu:main", lang)
        )
        await callback.answer()
        return

    text = t("favorites_list", lang) + format_movie_list(movies[:10], lang)

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=movies_list_keyboard(movies[:10], lang)
    )
    await callback.answer()


@router.callback_query(F.data == "menu:history")
async def show_history(callback: CallbackQuery, session: AsyncSession):
    """Show user watch history"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"

    movies = await get_user_history(session, callback.from_user.id)

    if not movies:
        text = t("history_empty", lang)
        await callback.message.edit_text(
            text,
            reply_markup=back_keyboard("menu:main", lang)
        )
        await callback.answer()
        return

    text = t("history_list", lang) + format_movie_list(movies[:10], lang)

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=movies_list_keyboard(movies[:10], lang)
    )
    await callback.answer()


# ==================== GENRES ====================

@router.callback_query(F.data == "menu:genres")
async def show_genres(callback: CallbackQuery, session: AsyncSession):
    """Show genres list"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"

    genres = await get_all_genres(session)

    if not genres:
        await callback.answer(t("no_movies", lang), show_alert=True)
        return

    await callback.message.edit_text(
        t("genres_list", lang),
        parse_mode="HTML",
        reply_markup=genres_keyboard(genres, lang)
    )
    await callback.answer()


# ==================== RANDOM ====================

@router.callback_query(F.data == "random")
async def show_random_movie(callback: CallbackQuery, session: AsyncSession):
    """Show random movie"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"

    movie = await get_random_movie(session)

    if not movie:
        await callback.answer(t("no_movies", lang), show_alert=True)
        return

    # Get genres
    genres = await get_movie_genres(session, movie.id)
    genre_names = ", ".join([g.get_name(lang) for g in genres]) if genres else "—"

    text = t("random_movie", lang) + "\n\n"
    text += t(
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

    from database.crud import is_favorite
    is_fav = await is_favorite(session, callback.from_user.id, movie.id)

    await callback.message.answer_video(
        video=movie.file_id,
        caption=text,
        parse_mode="HTML",
        reply_markup=movie_keyboard(movie.id, is_fav, lang)
    )
    await callback.answer()


# ==================== SETTINGS ====================

@router.callback_query(F.data == "menu:settings")
async def show_settings(callback: CallbackQuery, session: AsyncSession):
    """Show settings"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"

    text = ("⚙️ <b>Sozlamalar</b>" if lang == "uz"
            else "⚙️ <b>Настройки</b>" if lang == "ru"
    else "⚙️ <b>Settings</b>")

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=settings_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data == "settings:language")
async def show_language_settings(callback: CallbackQuery, session: AsyncSession):
    """Show language selection"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"

    await callback.message.edit_text(
        t("choose_language", lang),
        reply_markup=language_keyboard()
    )
    await callback.answer()