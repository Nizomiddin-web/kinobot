"""
Keyboards - Inline and Reply keyboards
"""

from typing import List, Optional

from aiogram import Bot
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from config import config, INTERFACE_LANGUAGES
from locales import t


# ==================== MAIN MENU ====================

def main_menu_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Main menu keyboard for /start"""
    builder = InlineKeyboardBuilder()

    # Row 1: Search and Random
    builder.button(text="🔍 Qidirish" if lang == "uz" else "🔍 Поиск" if lang == "ru" else "🔍 Search",
                   switch_inline_query_current_chat="")
    builder.button(text="🎲 Tasodifiy" if lang == "uz" else "🎲 Случайный" if lang == "ru" else "🎲 Random",
                   callback_data="random")

    # Row 2: Categories
    builder.button(text="🎬 Kino" if lang == "uz" else "🎬 Фильмы" if lang == "ru" else "🎬 Movies",
                   switch_inline_query_current_chat="!kino")
    builder.button(text="📺 Serial" if lang == "uz" else "📺 Сериалы" if lang == "ru" else "📺 Series",
                   switch_inline_query_current_chat="!serial")

    # Row 3: More categories
    # Row 3: More categories
    builder.button(text="🎌 Anime",
                   switch_inline_query_current_chat="!anime")
    builder.button(text="🧸 Multfilm" if lang == "uz" else "🧸 Мультфильм" if lang == "ru" else "🧸 Cartoon",
                   switch_inline_query_current_chat="!multfilm")

    # Row 4: Top and New
    builder.button(text="🏆 Top" if lang == "uz" else "🏆 Топ" if lang == "ru" else "🏆 Top",
                   switch_inline_query_current_chat="!top")
    builder.button(text="🆕 Yangi" if lang == "uz" else "🆕 Новые" if lang == "ru" else "🆕 New",
                   switch_inline_query_current_chat="!new")

    # Row 5: User's content - INLINE MODE
    builder.button(text="❤️ Sevimlilar" if lang == "uz" else "❤️ Избранное" if lang == "ru" else "❤️ Favorites",
                   switch_inline_query_current_chat="!fav")
    # builder.button(text="📜 Tarix" if lang == "uz" else "📜 История" if lang == "ru" else "📜 History",
    #                switch_inline_query_current_chat="!history")

    # Row 6: Genres and Settings
    builder.button(text="🎭 Janrlar" if lang == "uz" else "🎭 Жанры" if lang == "ru" else "🎭 Genres",
                   callback_data="menu:genres")
    builder.button(text="⚙️ Sozlamalar" if lang == "uz" else "⚙️ Настройки" if lang == "ru" else "⚙️ Settings",
                   callback_data="menu:settings")

    builder.adjust(2, 2, 2, 2, 2, 2)
    return builder.as_markup()


def settings_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Settings keyboard"""
    builder = InlineKeyboardBuilder()

    builder.button(text="🌐 Tilni o'zgartirish" if lang == "uz" else "🌐 Сменить язык" if lang == "ru" else "🌐 Change language",
                   callback_data="settings:language")
    builder.button(text="🔙 Orqaga" if lang == "uz" else "🔙 Назад" if lang == "ru" else "🔙 Back",
                   callback_data="menu:main")

    builder.adjust(1)
    return builder.as_markup()


def category_movies_keyboard(movies: list, category: str, lang: str = "uz", page: int = 1) -> InlineKeyboardMarkup:
    """Category movies keyboard with pagination"""
    builder = InlineKeyboardBuilder()

    for movie in movies:
        title = movie.get_title(lang)
        if len(title) > 30:
            title = title[:27] + "..."

        # Show episode count for series
        if movie.total_episodes > 0:
            builder.button(
                text=f"📺 {title} ({movie.total_episodes} qism)",
                callback_data=f"movie:{movie.id}"
            )
        else:
            builder.button(
                text=f"🎬 {title} ({movie.year})",
                callback_data=f"movie:{movie.id}"
            )

    # Navigation row
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="◀️", callback_data=f"catpage:{category}:{page-1}"))
    nav_buttons.append(InlineKeyboardButton(text=f"📄 {page}", callback_data="noop"))
    nav_buttons.append(InlineKeyboardButton(text="▶️", callback_data=f"catpage:{category}:{page+1}"))

    # Back button
    builder.adjust(1)
    builder.row(*nav_buttons)
    builder.button(text="🔙 Orqaga" if lang == "uz" else "🔙 Назад" if lang == "ru" else "🔙 Back",
                   callback_data="menu:main")

    return builder.as_markup()


# ==================== LANGUAGE ====================

def language_keyboard() -> InlineKeyboardMarkup:
    """Language selection keyboard"""
    builder = InlineKeyboardBuilder()

    for code, name in INTERFACE_LANGUAGES.items():
        builder.button(text=name, callback_data=f"lang:{code}")

    builder.adjust(3)
    return builder.as_markup()


# ==================== SUBSCRIPTION ====================

# def subscription_keyboard(channels: list, lang: str = "uz") -> InlineKeyboardMarkup:
#     """Subscription channels keyboard"""
#     builder = InlineKeyboardBuilder()
#
#     for channel in channels:
#         builder.button(
#             text=f"📢 {channel.channel_title}",
#             url=f"https://t.me/{channel.channel_username.lstrip('@')}"
#         )
#
#     builder.button(text=t("check_subscription", lang), callback_data="check_sub")
#
#     builder.adjust(1)
#     return builder.as_markup()

async def subscription_keyboard(bot: Bot, channels: list, lang: str = "uz") -> InlineKeyboardMarkup:
    """Subscription keyboard for public and private channels"""
    builder = InlineKeyboardBuilder()

    for channel in channels:
        username = getattr(channel, 'channel_username', False)

        if username and username.startswith("-100"):
            # Private channel - create or use existing invite link
            invite_link = getattr(channel, 'invite_link', None)

            if not invite_link:
                try:
                    chat_invite = await bot.create_chat_invite_link(
                        chat_id=channel.channel_id,
                        creates_join_request=False
                    )
                    invite_link = chat_invite.invite_link
                except Exception:
                    continue

            builder.button(
                text=f"🔒 {channel.channel_title}",
                url=invite_link
            )
        else:
            # Public channel
            if channel.channel_username:
                builder.button(
                    text=f"📢 {channel.channel_title}",
                    url=f"https://t.me/{channel.channel_username.lstrip('@')}"
                )

    builder.button(text=t("check_subscription", lang), callback_data="check_sub")
    builder.adjust(1)
    return builder.as_markup()


# ==================== MOVIE ====================

def movie_keyboard(
    movie_id: int,
    is_favorite: bool = False,
    lang: str = "uz",
    is_series: bool = False,
    total_episodes: int = 0
) -> InlineKeyboardMarkup:
    """Movie action keyboard"""
    builder = InlineKeyboardBuilder()

    # For series - show episodes button
    if is_series and total_episodes > 0:
        episodes_text = f"📋 Qismlar ({total_episodes})" if lang == "uz" else f"📋 Серии ({total_episodes})" if lang == "ru" else f"📋 Episodes ({total_episodes})"
        builder.button(text=episodes_text, callback_data=f"episodes:{movie_id}")
        builder.adjust(1)

    # Rating button
    builder.button(text=t("btn_rate", lang), callback_data=f"rate:{movie_id}")

    # Favorite button
    if is_favorite:
        builder.button(text=t("btn_unfavorite", lang), callback_data=f"unfav:{movie_id}")
    else:
        builder.button(text=t("btn_favorite", lang), callback_data=f"fav:{movie_id}")

    # Share button - inline switch
    share_text = "↪️ Ulashish" if lang == "uz" else "↪️ Поделиться" if lang == "ru" else "↪️ Share"
    builder.button(
        text=share_text,
        switch_inline_query=f"id:{movie_id}"
    )

    if is_series and total_episodes > 0:
        builder.adjust(1, 2, 1)
    else:
        builder.adjust(2, 1)

    return builder.as_markup()


# ==================== EPISODES ====================

def episodes_keyboard(
    episodes: list,
    movie_id: int,
    lang: str = "uz",
    season: int = 1,
    total_seasons: int = 1
) -> InlineKeyboardMarkup:
    """Episodes list keyboard"""
    builder = InlineKeyboardBuilder()

    # Season selector if multiple seasons
    if total_seasons > 1:
        season_buttons = []
        for s in range(1, total_seasons + 1):
            if s == season:
                season_buttons.append(
                    InlineKeyboardButton(text=f"📍 {s}-fasl", callback_data="noop")
                )
            else:
                season_buttons.append(
                    InlineKeyboardButton(text=f"{s}-fasl", callback_data=f"season:{movie_id}:{s}")
                )
        builder.row(*season_buttons[:5])  # Max 5 seasons per row

    # Episode buttons - 5 per row
    row_buttons = []
    for ep in episodes:
        btn_text = f"{ep.episode_number}"
        row_buttons.append(
            InlineKeyboardButton(text=btn_text, callback_data=f"ep:{ep.id}")
        )

        if len(row_buttons) == 5:
            builder.row(*row_buttons)
            row_buttons = []

    if row_buttons:
        builder.row(*row_buttons)

    # Download all button
    all_text = "📥 Hammasini yuklash" if lang == "uz" else "📥 Скачать все" if lang == "ru" else "📥 Download all"
    builder.button(text=all_text, callback_data=f"all_eps:{movie_id}:{season}")

    # Back button
    back_text = "🔙 Orqaga" if lang == "uz" else "🔙 Назад" if lang == "ru" else "🔙 Back"
    builder.button(text=back_text, callback_data=f"back")

    builder.adjust(1)

    return builder.as_markup()


def episode_keyboard(episode_id: int, movie_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    """Single episode keyboard"""
    builder = InlineKeyboardBuilder()

    # Back to episodes list
    back_text = "📋 Qismlarga" if lang == "uz" else "📋 К сериям" if lang == "ru" else "📋 To episodes"
    builder.button(text=back_text, callback_data=f"episodes:{movie_id}")

    return builder.as_markup()


def rating_keyboard(movie_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    """Rating stars keyboard"""
    builder = InlineKeyboardBuilder()

    for i in range(1, 6):
        stars = "⭐" * i
        builder.button(text=stars, callback_data=f"setrate:{movie_id}:{i}")

    builder.button(text=t("btn_back", lang), callback_data=f"movie:{movie_id}")

    builder.adjust(5, 1)
    return builder.as_markup()


def movies_list_keyboard(
    movies: list,
    lang: str = "uz",
    page: int = 1,
    total_pages: int = 1,
    callback_prefix: str = "movie"
) -> InlineKeyboardMarkup:
    """Movies list with pagination"""
    builder = InlineKeyboardBuilder()

    for movie in movies:
        title = movie.get_title(lang)
        if len(title) > 35:
            title = title[:32] + "..."

        if movie.total_episodes > 0:
            builder.button(
                text=f"📺 {title} ({movie.total_episodes} qism) {movie.rating_display}",
                callback_data=f"episodes:{movie.id}"
            )
        else:
            builder.button(
                text=f"🎬 {title} ({movie.year}) {movie.rating_display}",
                callback_data=f"{callback_prefix}:{movie.id}"
            )

    # Pagination
    nav_buttons = []
    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(text="◀️", callback_data=f"page:{page-1}")
        )

    nav_buttons.append(
        InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="noop")
    )

    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(text="▶️", callback_data=f"page:{page+1}")
        )

    builder.adjust(1)

    if total_pages > 1:
        builder.row(*nav_buttons)

    # Back button
    back_text = "🔙 Orqaga" if lang == "uz" else "🔙 Назад" if lang == "ru" else "🔙 Back"
    builder.button(text=back_text, callback_data="menu:main")

    return builder.as_markup()


# ==================== GENRES ====================

def genres_keyboard(genres: list, lang: str = "uz") -> InlineKeyboardMarkup:
    """Genres list keyboard"""
    builder = InlineKeyboardBuilder()

    for genre in genres:
        name = genre.get_name(lang)
        builder.button(text=name, callback_data=f"genre:{genre.id}")

    # Back button
    back_text = "🔙 Orqaga" if lang == "uz" else "🔙 Назад" if lang == "ru" else "🔙 Back"
    builder.button(text=back_text, callback_data="menu:main")

    builder.adjust(3, 3, 3, 3, 3, 1)
    return builder.as_markup()


def genres_select_keyboard(
    genres: list,
    selected: list = None,
    lang: str = "uz"
) -> InlineKeyboardMarkup:
    """Genre selection keyboard for adding movie"""
    builder = InlineKeyboardBuilder()
    selected = selected or []

    for genre in genres:
        name = genre.get_name(lang)
        if genre.id in selected:
            name = f"✅ {name}"
        builder.button(text=name, callback_data=f"selgenre:{genre.id}")

    builder.button(text=t("btn_save", lang), callback_data="save_genres")
    builder.button(text=t("btn_skip", lang), callback_data="skip_genres")

    builder.adjust(3, 3, 3, 3, 2)
    return builder.as_markup()


# ==================== CATEGORIES ====================

def categories_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Categories keyboard"""
    builder = InlineKeyboardBuilder()

    categories = [
        ("🎬 Kino", "Kino"),
        ("📺 Serial", "Serial"),
        ("🎌 Anime", "Anime"),
        ("🧸 Multfilm", "Multfilm")
    ]

    for name, cat in categories:
        builder.button(text=name, callback_data=f"cat:{cat}")

    builder.adjust(2, 2)
    return builder.as_markup()


# ==================== MOVIE ADD ====================

def year_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Year selection keyboard"""
    builder = InlineKeyboardBuilder()

    import datetime
    current_year = datetime.datetime.now().year

    for year in range(current_year, current_year - 5, -1):
        builder.button(text=str(year), callback_data=f"year:{year}")

    builder.button(text=t("btn_cancel", lang), callback_data="cancel_add")

    builder.adjust(5, 1)
    return builder.as_markup()


def movie_language_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Movie language selection keyboard"""
    builder = InlineKeyboardBuilder()

    languages = config.LANGUAGES

    for movie_lang in languages:
        builder.button(text=movie_lang, callback_data=f"mlang:{movie_lang}")

    builder.button(text=t("btn_cancel", lang), callback_data="cancel_add")

    builder.adjust(3, 3, 2)
    return builder.as_markup()


def quality_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Quality selection keyboard"""
    builder = InlineKeyboardBuilder()

    for quality in config.QUALITIES:
        builder.button(text=quality, callback_data=f"qual:{quality}")

    builder.button(text=t("btn_cancel", lang), callback_data="cancel_add")

    builder.adjust(5, 1)
    return builder.as_markup()


def category_select_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Category selection for adding movie"""
    builder = InlineKeyboardBuilder()

    for cat in config.CATEGORIES:
        emoji = {"Kino": "🎬","Anime": "🎌", "Multfilm": "🧸"}.get(cat, "🎬")
        builder.button(text=f"{emoji} {cat}", callback_data=f"mcat:{cat}")

    builder.button(text=t("btn_cancel", lang), callback_data="cancel_add")

    builder.adjust(2, 2, 1)
    return builder.as_markup()

def category_select_keyboard_2(lang: str = "uz") -> InlineKeyboardMarkup:
    """Category selection for adding movie"""
    builder = InlineKeyboardBuilder()

    for cat in config.CATEGORIES:
        emoji = {"Kino": "🎬", "Serial": "📺", "Anime": "🎌", "Multfilm": "🧸"}.get(cat, "🎬")
        builder.button(text=f"{emoji} {cat}", callback_data=f"mcat:{cat}")

    builder.button(text=t("btn_cancel", lang), callback_data="cancel_add")

    builder.adjust(2, 2, 1)
    return builder.as_markup()


def skip_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Skip button keyboard"""
    builder = InlineKeyboardBuilder()
    builder.button(text=t("btn_skip", lang), callback_data="skip")
    builder.button(text=t("btn_cancel", lang), callback_data="cancel_add")
    builder.adjust(2)
    return builder.as_markup()


def confirm_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Confirm/Cancel keyboard"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Ha", callback_data="confirm")
    builder.button(text="❌ Yo'q", callback_data="cancel")
    builder.adjust(2)
    return builder.as_markup()


# ==================== ADMIN ====================

def admin_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Admin panel keyboard"""
    builder = InlineKeyboardBuilder()

    buttons = [
        ("📊 Statistika", "admin:stats"),
        ("🎬 Kinolar", "admin:movies"),
        ("📢 Kanallar", "admin:channels"),
        ("📨 Xabar yuborish", "admin:broadcast"),
        ("🏆 Top foydalanuvchilar", "admin:top_users"),
        ("👥 Adminlar", "admin:admins"),
    ]

    for text, data in buttons:
        builder.button(text=text, callback_data=data)

    builder.adjust(2, 2, 2)
    return builder.as_markup()


def channels_admin_keyboard(channels: list, lang: str = "uz") -> InlineKeyboardMarkup:
    """Admin channels management keyboard"""
    builder = InlineKeyboardBuilder()

    for channel in channels:
        status = "✅" if channel.is_active else "❌"
        builder.button(
            text=f"{status} {channel.channel_title}",
            callback_data=f"ch_toggle:{channel.channel_id}"
        )

    builder.button(text="➕ Kanal qo'shish", callback_data="ch_add")
    builder.button(text=t("btn_back", lang), callback_data="admin:panel")

    builder.adjust(1)
    return builder.as_markup()


# ==================== INLINE MODE ====================

def inline_movie_keyboard(movie_id: int, bot_username: str = "") -> InlineKeyboardMarkup:
    """Keyboard for inline query result"""
    builder = InlineKeyboardBuilder()

    # Button to get movie in bot
    if bot_username:
        builder.button(
            text="🎬 Kinoni olish",
            url=f"https://t.me/{bot_username}?start=movie_{movie_id}"
        )
    else:
        builder.button(text="🎬 Kinoni olish", callback_data=f"get:{movie_id}")

    return builder.as_markup()


# ==================== CANCEL / BACK ====================

def cancel_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Cancel keyboard"""
    builder = InlineKeyboardBuilder()
    builder.button(text=t("btn_cancel", lang), callback_data="cancel")
    return builder.as_markup()


def back_keyboard(callback_data: str, lang: str = "uz") -> InlineKeyboardMarkup:
    """Back button keyboard"""
    builder = InlineKeyboardBuilder()
    builder.button(text=t("btn_back", lang), callback_data=callback_data)
    return builder.as_markup()