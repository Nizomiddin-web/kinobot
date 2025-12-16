"""
Admin handlers - Movie management
Supports: Caption parsing, Inline buttons, Minimal mode
"""

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from config import config
from database.crud import (
    get_user, is_admin, create_movie, update_movie, delete_movie,
    get_all_genres, add_movie_genre, get_genre_by_name, get_movie
)
from keyboards import (
    year_keyboard, movie_language_keyboard, quality_keyboard,
    category_select_keyboard, genres_select_keyboard, skip_keyboard,
    cancel_keyboard
)
from locales import t
from states import MovieAddState
from utils import parse_movie_caption, get_file_id_from_message, detect_category_from_genres
from handlers.admin.panel import check_admin

router = Router()


# ==================== CHANNEL POST HANDLER ====================

@router.channel_post(F.video | F.document | F.animation)
async def handle_channel_video(message: Message, session: AsyncSession, bot: Bot):
    """
    Handle video posted to movie channel
    Auto-detects and processes new movies
    """
    # Check if message is from movie channel
    if message.chat.id != config.MOVIE_CHANNEL_ID:
        return
    
    file_id = get_file_id_from_message(message)
    if not file_id:
        return
    
    # Get thumbnail
    from utils import get_thumbnail_from_message
    thumbnail_file_id = get_thumbnail_from_message(message)

    # Get thumbnail URL
    thumbnail_url = None
    if thumbnail_file_id:
        try:
            file = await bot.get_file(thumbnail_file_id)
            if file.file_path:
                thumbnail_url = f"https://api.telegram.org/file/bot{config.BOT_TOKEN}/{file.file_path}"
        except:
            pass

    caption = message.caption or ""

    # Try to parse caption
    parsed = parse_movie_caption(caption)

    if parsed["title"]:
        # Caption has movie info - auto create
        movie = await create_movie(
            session,
            title=parsed["title"],
            file_id=file_id,
            thumbnail_file_id=thumbnail_file_id,
            thumbnail_url=thumbnail_url,
            message_id=message.message_id,
            channel_id=message.chat.id,
            added_by=0,  # System added
            year=parsed["year"],
            language=parsed["language"],
            quality=parsed["quality"],
            duration=parsed["duration"],
            caption=parsed["caption"],
            category=detect_category_from_genres(parsed["genres"])
        )

        # Add genres
        for genre_name in parsed["genres"]:
            genre = await get_genre_by_name(session, genre_name)
            if genre:
                await add_movie_genre(session, movie.id, genre.id)

        # Notify in channel
        await message.reply(
            f"✅ Kino qo'shildi!\n🆔 Kod: <code>{movie.id}</code>",
            parse_mode="HTML"
        )
    else:
        # No caption parsing possible - just notify
        # Admin can manually add via FSM
        await message.reply(
            f"📽 Video aniqlandi.\n\n"
            f"Kino qo'shish uchun caption formatida yuboring:\n"
            f"<code>Kino nomi | 2024 | Action, Drama | O'zbek | 1080p</code>\n\n"
            f"Yoki admin botda /add_movie buyrug'ini ishlating.",
            parse_mode="HTML"
        )


# ==================== MANUAL ADD MOVIE ====================

@router.message(Command("add_movie"))
async def cmd_add_movie(message: Message, state: FSMContext, session: AsyncSession):
    """Start manual movie adding process"""
    user = await get_user(session, message.from_user.id)
    lang = user.language if user else "uz"

    if not await check_admin(session, message.from_user.id):
        await message.answer(t("not_admin", lang))
        return

    await state.set_state(MovieAddState.waiting_title)
    await state.update_data(lang=lang)

    await message.answer(
        "📽 Kino qo'shish\n\n"
        "Avval kanalga video yuboring, so'ng uning message_id sini kiriting.\n"
        "Yoki to'g'ridan-to'g'ri video yuboring.\n\n"
        "Kino nomini kiriting:",
        reply_markup=cancel_keyboard(lang)
    )


@router.message(MovieAddState.waiting_title, F.text)
async def process_title(message: Message, state: FSMContext, session: AsyncSession):
    """Process movie title"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    title = message.text.strip()

    if len(title) < 2:
        await message.answer(t("invalid_input", lang))
        return

    await state.update_data(title=title)
    await state.set_state(MovieAddState.waiting_year)

    await message.answer(
        t("enter_year", lang),
        reply_markup=year_keyboard(lang)
    )


@router.message(MovieAddState.waiting_title, F.video | F.document)
async def process_video_direct(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    """Process directly sent video"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    file_id = get_file_id_from_message(message)

    if not file_id:
        await message.answer(t("invalid_input", lang))
        return

    # Get thumbnail
    from utils import get_thumbnail_from_message
    thumbnail_file_id = get_thumbnail_from_message(message)

    # Get thumbnail URL
    thumbnail_url = None
    if thumbnail_file_id:
        try:
            file = await bot.get_file(thumbnail_file_id)
            if file.file_path:
                thumbnail_url = f"https://api.telegram.org/file/bot{config.BOT_TOKEN}/{file.file_path}"
        except:
            pass

    # Forward to channel first
    try:
        forwarded = await message.forward(config.MOVIE_CHANNEL_ID)

        await state.update_data(
            file_id=file_id,
            thumbnail_file_id=thumbnail_file_id,
            thumbnail_url=thumbnail_url,
            message_id=forwarded.message_id,
            channel_id=config.MOVIE_CHANNEL_ID
        )

        await message.answer(
            "✅ Video kanalga yuborildi.\n\nEndi kino nomini kiriting:",
            reply_markup=cancel_keyboard(lang)
        )
    except Exception as e:
        await message.answer(
            f"❌ Videoni kanalga yuborishda xato: {e}\n"
            f"Avval videoni kanalga qo'lda yuboring."
        )


@router.callback_query(F.data.startswith("year:"), MovieAddState.waiting_year)
async def process_year_callback(callback: CallbackQuery, state: FSMContext):
    """Process year from callback"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    year = int(callback.data.split(":")[1])

    await state.update_data(year=year)
    await state.set_state(MovieAddState.waiting_language)

    await callback.message.edit_text(
        t("select_language", lang),
        reply_markup=movie_language_keyboard(lang)
    )
    await callback.answer()


@router.message(MovieAddState.waiting_year, F.text)
async def process_year_text(message: Message, state: FSMContext):
    """Process year from text"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    from utils import validate_year
    year = validate_year(message.text)

    if not year:
        await message.answer(t("invalid_input", lang))
        return

    await state.update_data(year=year)
    await state.set_state(MovieAddState.waiting_language)

    await message.answer(
        t("select_language", lang),
        reply_markup=movie_language_keyboard(lang)
    )


@router.callback_query(F.data.startswith("mlang:"), MovieAddState.waiting_language)
async def process_language(callback: CallbackQuery, state: FSMContext):
    """Process movie language"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    movie_lang = callback.data.split(":")[1]

    await state.update_data(movie_language=movie_lang)
    await state.set_state(MovieAddState.waiting_quality)

    await callback.message.edit_text(
        t("select_quality", lang),
        reply_markup=quality_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("qual:"), MovieAddState.waiting_quality)
async def process_quality(callback: CallbackQuery, state: FSMContext):
    """Process movie quality"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    quality = callback.data.split(":")[1]

    await state.update_data(quality=quality)
    await state.set_state(MovieAddState.waiting_category)

    await callback.message.edit_text(
        t("select_category", lang),
        reply_markup=category_select_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("mcat:"), MovieAddState.waiting_category)
async def process_category(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Process movie category"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    category = callback.data.split(":")[1]

    await state.update_data(category=category, selected_genres=[])
    await state.set_state(MovieAddState.waiting_genres)

    genres = await get_all_genres(session)

    await callback.message.edit_text(
        t("select_genres", lang),
        reply_markup=genres_select_keyboard(genres, [], lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("selgenre:"), MovieAddState.waiting_genres)
async def toggle_genre(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Toggle genre selection"""
    data = await state.get_data()
    lang = data.get("lang", "uz")
    selected = data.get("selected_genres", [])

    genre_id = int(callback.data.split(":")[1])

    if genre_id in selected:
        selected.remove(genre_id)
    else:
        selected.append(genre_id)

    await state.update_data(selected_genres=selected)

    genres = await get_all_genres(session)

    await callback.message.edit_reply_markup(
        reply_markup=genres_select_keyboard(genres, selected, lang)
    )
    await callback.answer()


@router.callback_query(F.data.in_(["save_genres", "skip_genres"]), MovieAddState.waiting_genres)
async def process_genres_done(callback: CallbackQuery, state: FSMContext):
    """Finish genre selection"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    await state.set_state(MovieAddState.waiting_duration)

    await callback.message.edit_text(
        t("enter_duration", lang),
        reply_markup=skip_keyboard(lang)
    )
    await callback.answer()


@router.message(MovieAddState.waiting_duration, F.text)
async def process_duration(message: Message, state: FSMContext):
    """Process duration and ask for poster"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    from utils import validate_duration
    duration = validate_duration(message.text)

    await state.update_data(duration=duration)
    await state.set_state(MovieAddState.waiting_poster)

    await message.answer(
        "🖼 Kino posterini yuboring (rasm yoki URL)\n\nYoki o'tkazib yuboring:",
        reply_markup=skip_keyboard(lang)
    )


@router.callback_query(F.data == "skip", MovieAddState.waiting_duration)
async def skip_duration(callback: CallbackQuery, state: FSMContext):
    """Skip duration and ask for poster"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    await state.update_data(duration=None)
    await state.set_state(MovieAddState.waiting_poster)

    await callback.message.edit_text(
        "🖼 Kino posterini yuboring (rasm yoki URL)\n\nYoki o'tkazib yuboring:",
        reply_markup=skip_keyboard(lang)
    )
    await callback.answer()


@router.message(MovieAddState.waiting_poster, F.photo)
async def process_poster_photo(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    """Process poster photo"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    # Get largest photo
    photo = message.photo[-1]

    # Get file URL
    try:
        file = await bot.get_file(photo.file_id)
        if file.file_path:
            poster_url = f"https://api.telegram.org/file/bot{config.BOT_TOKEN}/{file.file_path}"
            await state.update_data(poster_url=poster_url)
    except:
        pass

    # Save movie
    await save_movie(message, state, session)


@router.message(MovieAddState.waiting_poster, F.text)
async def process_poster_url(message: Message, state: FSMContext, session: AsyncSession):
    """Process poster URL"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    url = message.text.strip()

    # Check if it's a valid URL
    if url.startswith(("http://", "https://")):
        await state.update_data(poster_url=url)

    # Save movie
    await save_movie(message, state, session)


@router.callback_query(F.data == "skip", MovieAddState.waiting_poster)
async def skip_poster(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Skip poster and save movie"""
    await state.update_data(poster_url=None)

    # Save movie
    await save_movie(callback.message, state, session, callback.from_user.id)
    await callback.answer()


async def save_movie(message: Message, state: FSMContext, session: AsyncSession, user_id: int = None):
    """Save movie to database"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    if user_id is None:
        user_id = message.from_user.id

    # Check if we have file info
    file_id = data.get("file_id")
    thumbnail_file_id = data.get("thumbnail_file_id")
    thumbnail_url = data.get("thumbnail_url") or data.get("poster_url")  # poster_url ham tekshiriladi
    message_id = data.get("message_id")
    channel_id = data.get("channel_id", config.MOVIE_CHANNEL_ID)

    if not file_id or not message_id:
        await message.answer(
            "❌ Video ma'lumotlari topilmadi.\n"
            "Avval kanalga video yuboring."
        )
        await state.clear()
        return

    # Create movie
    movie = await create_movie(
        session,
        title=data["title"],
        file_id=file_id,
        thumbnail_file_id=thumbnail_file_id,
        thumbnail_url=thumbnail_url,
        message_id=message_id,
        channel_id=channel_id,
        added_by=user_id,
        year=data.get("year", 2024),
        language=data.get("movie_language", "O'zbek"),
        quality=data.get("quality", "1080p"),
        duration=data.get("duration"),
        category=data.get("category", "Kino")
    )

    # Add genres
    for genre_id in data.get("selected_genres", []):
        await add_movie_genre(session, movie.id, genre_id)

    await state.clear()

    await message.answer(
        t("movie_added", lang, id=movie.id),
        parse_mode="HTML"
    )


# ==================== CANCEL ====================

@router.callback_query(F.data == "cancel_add")
async def cancel_add_movie(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Cancel movie adding"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"

    await state.clear()
    await callback.message.edit_text(t("movie_add_cancelled", lang))
    await callback.answer()


# ==================== DELETE MOVIE ====================

@router.message(Command("delete_movie"))
async def cmd_delete_movie(message: Message, session: AsyncSession):
    """Delete movie command"""
    user = await get_user(session, message.from_user.id)
    lang = user.language if user else "uz"

    if not await check_admin(session, message.from_user.id):
        await message.answer(t("not_admin", lang))
        return

    # Extract movie ID from command
    parts = message.text.split()

    if len(parts) < 2:
        await message.answer("Foydalanish: /delete_movie [id]")
        return

    try:
        movie_id = int(parts[1])
    except ValueError:
        await message.answer(t("invalid_input", lang))
        return

    movie = await get_movie(session, movie_id)

    if not movie:
        await message.answer(t("movie_not_found", lang))
        return

    await delete_movie(session, movie_id)

    await message.answer(t("movie_deleted", lang))


# ==================== EDIT MOVIE ====================

@router.message(F.text.regexp(r'^/edit_(\d+)$'))
async def cmd_edit_movie(message: Message, session: AsyncSession):
    """Edit movie command"""
    import re

    user = await get_user(session, message.from_user.id)
    lang = user.language if user else "uz"

    if not await check_admin(session, message.from_user.id):
        await message.answer(t("not_admin", lang))
        return

    match = re.match(r'^/edit_(\d+)$', message.text)
    movie_id = int(match.group(1))

    movie = await get_movie(session, movie_id)

    if not movie:
        await message.answer(t("movie_not_found", lang))
        return

    # Show current info and edit options
    text = f"""📝 <b>Kino tahrirlash</b>

🆔 ID: {movie.id}
📽 Nom: {movie.title}
📅 Yil: {movie.year}
🌐 Til: {movie.language}
📺 Sifat: {movie.quality}
📁 Kategoriya: {movie.category}

Tahrirlash uchun quyidagi formatda yuboring:
<code>/set_{movie.id}_title Yangi nom</code>
<code>/set_{movie.id}_year 2024</code>
<code>/set_{movie.id}_language O'zbek</code>
<code>/set_{movie.id}_quality 1080p</code>
"""

    await message.answer(text, parse_mode="HTML")


@router.message(F.text.regexp(r'^/set_(\d+)_(\w+)\s+(.+)$'))
async def cmd_set_movie_field(message: Message, session: AsyncSession):
    """Set movie field"""
    import re

    user = await get_user(session, message.from_user.id)
    lang = user.language if user else "uz"

    if not await check_admin(session, message.from_user.id):
        await message.answer(t("not_admin", lang))
        return

    match = re.match(r'^/set_(\d+)_(\w+)\s+(.+)$', message.text)
    movie_id = int(match.group(1))
    field = match.group(2)
    value = match.group(3).strip()

    allowed_fields = ["title", "year", "language", "quality", "category", "duration"]

    if field not in allowed_fields:
        await message.answer(f"❌ Noto'g'ri maydon. Ruxsat etilgan: {', '.join(allowed_fields)}")
        return

    movie = await get_movie(session, movie_id)

    if not movie:
        await message.answer(t("movie_not_found", lang))
        return

    # Convert value if needed
    if field == "year":
        value = int(value)
    elif field == "duration":
        value = int(value)

    await update_movie(session, movie_id, **{field: value})

    await message.answer(f"✅ Kino #{movie_id} yangilandi: {field} = {value}")