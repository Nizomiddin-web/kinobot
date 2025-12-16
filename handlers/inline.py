"""
Inline query handler
"""

import urllib.parse
from aiogram import Router, Bot
from aiogram.types import (
    InlineQuery, InlineQueryResultArticle,
    InputTextMessageContent, InlineQueryResultPhoto
)
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import search_movies, get_user, get_movie, get_user_favorites, get_user_history, \
    get_movies_by_category, get_new_movies, get_top_movies
from keyboards import inline_movie_keyboard
from config import config

router = Router()


def get_placeholder_image(title: str, year: int) -> str:
    """Generate placeholder image URL with movie title"""
    text = urllib.parse.quote(f"{title[:12]}...\n{year}")
    return f"https://placehold.co/300x450/1a1a2e/ffffff?text={text}&font=roboto"


def build_movie_result(movie, lang: str, bot_username: str, prefix: str = "") -> InlineQueryResultArticle:
    """Build inline query result for a movie"""
    title = movie.get_title(lang)

    # Build description
    desc_parts = [str(movie.year)]
    if movie.language:
        desc_parts.append(movie.language)
    if movie.quality:
        desc_parts.append(movie.quality)
    desc_parts.append(f"👁 {movie.views}")

    description = " | ".join(desc_parts)

    # Message content
    message_text = f"""🎬 <b>{title}</b>

📅 Yil: {movie.year}
🌐 Til: {movie.language}
📺 Sifat: {movie.quality}

⭐ Reyting: {movie.rating_display}
👁 Ko'rishlar: {movie.views}

🎥 Kinoni ko'rish uchun tugmani bosing 👇"""

    # Use saved poster URL or placeholder
    if movie.thumbnail_url:
        thumb_url = movie.thumbnail_url
    else:
        thumb_url = get_placeholder_image(title, movie.year)

    display_title = f"{prefix}🎬 {title} ({movie.year})" if prefix else f"🎬 {title} ({movie.year})"

    return InlineQueryResultArticle(
        id=str(movie.id),
        title=display_title,
        description=description,
        input_message_content=InputTextMessageContent(
            message_text=message_text,
            parse_mode="HTML"
        ),
        reply_markup=inline_movie_keyboard(movie.id, bot_username),
        thumbnail_url=thumb_url,
        thumbnail_width=300,
        thumbnail_height=450
    )


@router.inline_query()
async def process_inline_query(inline_query: InlineQuery, session: AsyncSession, bot: Bot):
    """Process inline search query"""
    query = inline_query.query.strip()

    # Get bot username for deep links
    bot_info = await bot.get_me()
    bot_username = bot_info.username

    # Get user language
    user = await get_user(session, inline_query.from_user.id)
    lang = user.language if user else "uz"

    results = []

    # ==================== FAVORITES ====================
    if query == "!fav" or query.startswith("!fav "):
        movies = await get_user_favorites(session, inline_query.from_user.id, limit=50)

        if not movies:
            results.append(
                InlineQueryResultArticle(
                    id="empty_fav",
                    title="❤️ Sevimlilar bo'sh" if lang == "uz" else "❤️ Избранное пусто" if lang == "ru" else "❤️ Favorites empty",
                    description="Hali sevimli kinolar yo'q" if lang == "uz" else "Нет избранных фильмов" if lang == "ru" else "No favorite movies yet",
                    input_message_content=InputTextMessageContent(
                        message_text="Sevimlilar ro'yxati bo'sh"
                    ),
                    thumbnail_url="https://placehold.co/300x450/1a1a2e/ffffff?text=❤️&font=roboto"
                )
            )
        else:
            for movie in movies:
                results.append(build_movie_result(movie, lang, bot_username, "❤️ "))

    # Search for only kino
    elif query == "!kino" or query.startswith("!kino "):
        movies = await get_movies_by_category(session, "Kino", limit=50)

        if not movies:
            results.append(
                InlineQueryResultArticle(
                    id="empty_kino",
                    title="🎬 Kinolar yo'q" if lang == "uz" else "🎬 Нет фильмов",
                    description="Hali kinolar qo'shilmagan",
                    input_message_content=InputTextMessageContent(
                        message_text="Kinolar ro'yxati bo'sh"
                    ),
                    thumbnail_url="https://placehold.co/300x450/1a1a2e/ffffff?text=🎬"
                )
            )
        else:
            for movie in movies:
                results.append(build_movie_result(movie, lang, bot_username))

    # ==================== SERIAL (Series) ====================
    elif query == "!serial" or query.startswith("!serial "):
        movies = await get_movies_by_category(session, "Serial", limit=50)

        if not movies:
            results.append(
                InlineQueryResultArticle(
                    id="empty_serial",
                    title="📺 Seriallar yo'q" if lang == "uz" else "📺 Нет сериалов",
                    description="Hali seriallar qo'shilmagan",
                    input_message_content=InputTextMessageContent(
                        message_text="Seriallar ro'yxati bo'sh"
                    ),
                    thumbnail_url="https://placehold.co/300x450/1a1a2e/ffffff?text=📺"
                )
            )
        else:
            for movie in movies:
                results.append(build_movie_result(movie, lang, bot_username))

    # ==================== TOP ====================
    elif query == "!top" or query.startswith("!top "):
        movies = await get_top_movies(session, limit=50)

        if not movies:
            results.append(
                InlineQueryResultArticle(
                    id="empty_top",
                    title="🏆 Top kinolar yo'q" if lang == "uz" else "🏆 Нет топ фильмов",
                    description="Hali baholangan kinolar yo'q",
                    input_message_content=InputTextMessageContent(
                        message_text="Top kinolar ro'yxati bo'sh"
                    ),
                    thumbnail_url="https://placehold.co/300x450/1a1a2e/ffffff?text=🏆"
                )
            )
        else:
            for i, movie in enumerate(movies, 1):
                results.append(build_movie_result(movie, lang, bot_username, f"#{i} "))

    # ==================== NEW ====================
    elif query == "!new" or query.startswith("!new "):
        movies = await get_new_movies(session, limit=50)

        if not movies:
            results.append(
                InlineQueryResultArticle(
                    id="empty_new",
                    title="🆕 Yangi kinolar yo'q" if lang == "uz" else "🆕 Нет новых фильмов",
                    description="Hali kinolar qo'shilmagan",
                    input_message_content=InputTextMessageContent(
                        message_text="Yangi kinolar ro'yxati bo'sh"
                    ),
                    thumbnail_url="https://placehold.co/300x450/1a1a2e/ffffff?text=🆕"
                )
            )
        else:
            for movie in movies:
                results.append(build_movie_result(movie, lang, bot_username, "🆕 "))

    # ==================== HISTORY ====================
    elif query == "!history" or query.startswith("!history "):
        movies = await get_user_history(session, inline_query.from_user.id, limit=50)

        if not movies:
            results.append(
                InlineQueryResultArticle(
                    id="empty_history",
                    title="📜 Tarix bo'sh" if lang == "uz" else "📜 История пуста" if lang == "ru" else "📜 History empty",
                    description="Hali ko'rilgan kinolar yo'q" if lang == "uz" else "Нет просмотренных фильмов" if lang == "ru" else "No watched movies yet",
                    input_message_content=InputTextMessageContent(
                        message_text="Ko'rish tarixi bo'sh"
                    ),
                    thumbnail_url="https://placehold.co/300x450/1a1a2e/ffffff?text=📜&font=roboto"
                )
            )
        else:
            for movie in movies:
                results.append(build_movie_result(movie, lang, bot_username, "📜 "))

    # ==================== SHARE BY ID ====================
    elif query.startswith("id:"):
        movie_id_str = query[3:].strip()
        if movie_id_str.isdigit():
            movie = await get_movie(session, int(movie_id_str))
            if movie:
                title = movie.get_title(lang)

                # Build description
                desc_parts = [str(movie.year)]
                if movie.language:
                    desc_parts.append(movie.language)
                if movie.quality:
                    desc_parts.append(movie.quality)
                desc_parts.append(movie.rating_display)

                description = " | ".join(desc_parts)

                # Message for sharing
                message_text = f"""🎬 <b>{title}</b>

📅 Yil: {movie.year}
🌐 Til: {movie.language}
📺 Sifat: {movie.quality}
⭐ Reyting: {movie.rating_display}

🎥 Kinoni ko'rish uchun tugmani bosing 👇"""

                # Use saved poster URL or placeholder
                if movie.thumbnail_url:
                    thumb_url = movie.thumbnail_url
                else:
                    thumb_url = get_placeholder_image(title, movie.year)

                results.append(
                    InlineQueryResultArticle(
                        id=str(movie.id),
                        title=f"📤 Ulashish: {title} ({movie.year})",
                        description=description,
                        input_message_content=InputTextMessageContent(
                            message_text=message_text,
                            parse_mode="HTML"
                        ),
                        reply_markup=inline_movie_keyboard(movie.id, bot_username),
                        thumbnail_url=thumb_url,
                        thumbnail_width=300,
                        thumbnail_height=450
                    )
                )

        if not results:
            results.append(
                InlineQueryResultArticle(
                    id="not_found",
                    title="😔 Kino topilmadi",
                    description="Bunday ID li kino mavjud emas",
                    input_message_content=InputTextMessageContent(
                        message_text="Kino topilmadi"
                    )
                )
            )

    # ==================== SEARCH ====================
    elif len(query) < 2:
        # Show hint
        results.append(
            InlineQueryResultArticle(
                id="hint",
                title="🔍 Kino qidirish" if lang == "uz" else "🔍 Поиск фильма" if lang == "ru" else "🔍 Search movie",
                description="Kamida 2 ta belgi kiriting" if lang == "uz" else "Введите минимум 2 символа" if lang == "ru" else "Enter at least 2 characters",
                input_message_content=InputTextMessageContent(
                    message_text="Kino qidirish uchun @botni yozing va kino nomini kiriting"
                ),
                thumbnail_url="https://placehold.co/300x450/1a1a2e/ffffff?text=🔍&font=roboto"
            )
        )
    else:
        # Search movies
        movies = await search_movies(session, query, limit=50)

        if not movies:
            results.append(
                InlineQueryResultArticle(
                    id="not_found",
                    title="😔 Topilmadi" if lang == "uz" else "😔 Не найдено" if lang == "ru" else "😔 Not found",
                    description=f'"{query}" bo\'yicha hech narsa topilmadi',
                    input_message_content=InputTextMessageContent(
                        message_text=f'"{query}" bo\'yicha kino topilmadi'
                    ),
                    thumbnail_url="https://placehold.co/300x450/1a1a2e/ffffff?text=404&font=roboto"
                )
            )
        else:
            for movie in movies:
                results.append(build_movie_result(movie, lang, bot_username))

    await inline_query.answer(
        results[:50],
        cache_time=config.INLINE_CACHE_TIME if not query.startswith("!") else 5,  # Short cache for personal lists
        is_personal=True
    )