"""
Admin handlers - Serial and Episode management
"""
import re

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from config import config
from database.crud import (
    get_user, is_admin, create_movie, update_movie, get_movie,
    create_episode, get_episodes_by_movie, delete_episode,
    get_all_genres, add_movie_genre
)
from keyboards import (
    skip_keyboard, cancel_keyboard, category_select_keyboard,
    genres_select_keyboard, quality_keyboard, movie_language_keyboard,
    year_keyboard, confirm_keyboard
)
from locales import t
from utils import get_file_id_from_message, get_thumbnail_from_message

router = Router()


class SerialAddState(StatesGroup):
    """States for adding serial"""
    waiting_title = State()
    waiting_year = State()
    waiting_language = State()
    waiting_quality = State()
    waiting_genres = State()
    waiting_poster = State()


class EpisodeAddState(StatesGroup):
    """States for adding episode"""
    waiting_serial_id = State()
    waiting_season = State()
    waiting_episode_number = State()
    waiting_video = State()
    waiting_more = State()


async def check_admin(session: AsyncSession, user_id: int) -> bool:
    """Check if user is admin"""
    if user_id in config.SUPER_ADMIN_IDS:
        return True
    return await is_admin(session, user_id)


# ==================== ADD SERIAL ====================

@router.message(Command("add_serial"))
async def cmd_add_serial(message: Message, state: FSMContext, session: AsyncSession):
    """Start adding new serial"""
    user = await get_user(session, message.from_user.id)
    lang = user.language if user else "uz"

    if not await check_admin(session, message.from_user.id):
        await message.answer(t("not_admin", lang))
        return

    await state.set_state(SerialAddState.waiting_title)
    await state.update_data(lang=lang, category="Serial")

    await message.answer(
        "📺 <b>Yangi serial qo'shish</b>\n\n"
        "Serial nomini kiriting:",
        parse_mode="HTML",
        reply_markup=cancel_keyboard(lang)
    )


@router.message(SerialAddState.waiting_title, F.text)
async def process_serial_title(message: Message, state: FSMContext):
    """Process serial title"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    title = message.text.strip()

    if len(title) < 2:
        await message.answer(t("invalid_input", lang))
        return

    await state.update_data(title=title)
    await state.set_state(SerialAddState.waiting_year)

    await message.answer(
        "📅 Yilni tanlang yoki yozing:",
        reply_markup=year_keyboard(lang)
    )

@router.callback_query(F.data.stra, SerialAddState.waiting_year)
async def process_serial_year(callback: CallbackQuery, state: FSMContext):
    """Process serial year"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    year = int(callback.data.split(":")[1])
    await state.update_data(year=year)
    await state.set_state(SerialAddState.waiting_language)

    await callback.message.edit_text(
        "🌐 Tilni tanlang:",
        reply_markup=movie_language_keyboard(lang)
    )
    await callback.answer()

@router.message(F.text, SerialAddState.waiting_year)
async def process_serial_year(message: Message, state: FSMContext):
    """Process serial year"""
    year = message.text.strip()
    data = await state.get_data()
    lang = data.get("lang", "uz")
    if re.fullmatch(r"\d{4}", year):
        try:
            year = int(year)
            if 1900<=year<=2100:
                await state.update_data(year=year)
                await state.set_state(SerialAddState.waiting_language)

                await message.answer(
                    "🌐 Tilni tanlang:",
                    reply_markup=movie_language_keyboard(lang)
                )
            else:
                await message.answer("Yil xato kiritildi qaytadan kiriting!")

        except ValueError:
            await message.answer("Yil xato kiritildi qaytadan yozing!")






@router.callback_query(F.data.startswith("mlang:"), SerialAddState.waiting_language)
async def process_serial_language(callback: CallbackQuery, state: FSMContext):
    """Process serial language"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    movie_lang = callback.data.split(":")[1]
    await state.update_data(movie_language=movie_lang)
    await state.set_state(SerialAddState.waiting_quality)

    await callback.message.edit_text(
        "📺 Sifatni tanlang:",
        reply_markup=quality_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("qual:"), SerialAddState.waiting_quality)
async def process_serial_quality(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Process serial quality"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    quality = callback.data.split(":")[1]
    await state.update_data(quality=quality, selected_genres=[])
    await state.set_state(SerialAddState.waiting_genres)

    genres = await get_all_genres(session)

    await callback.message.edit_text(
        "🎭 Janrlarni tanlang:",
        reply_markup=genres_select_keyboard(genres, [], lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("selgenre:"), SerialAddState.waiting_genres)
async def toggle_serial_genre(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
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


@router.callback_query(F.data.in_(["save_genres", "skip_genres"]), SerialAddState.waiting_genres)
async def process_serial_genres_done(callback: CallbackQuery, state: FSMContext):
    """Finish genre selection"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    await state.set_state(SerialAddState.waiting_poster)

    await callback.message.edit_text(
        "🖼 Serial posterini yuboring (rasm yoki URL)\n\nYoki o'tkazib yuboring:",
        reply_markup=skip_keyboard(lang)
    )
    await callback.answer()


@router.message(SerialAddState.waiting_poster, F.photo)
async def process_serial_poster(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    """Process serial poster photo"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    photo = message.photo[-1]

    try:
        file = await bot.get_file(photo.file_id)
        if file.file_path:
            poster_url = f"https://api.telegram.org/file/bot{config.BOT_TOKEN}/{file.file_path}"
            await state.update_data(poster_url=poster_url, thumbnail_file_id=photo.file_id)
    except:
        pass

    await save_serial(message, state, session)


@router.message(SerialAddState.waiting_poster, F.text)
async def process_serial_poster_url(message: Message, state: FSMContext, session: AsyncSession):
    """Process serial poster URL"""
    url = message.text.strip()

    if url.startswith(("http://", "https://")):
        await state.update_data(poster_url=url)

    await save_serial(message, state, session)


@router.callback_query(F.data == "skip", SerialAddState.waiting_poster)
async def skip_serial_poster(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Skip poster and save serial"""
    await save_serial(callback.message, state, session, callback.from_user.id)
    await callback.answer()


async def save_serial(message: Message, state: FSMContext, session: AsyncSession, user_id: int = None):
    """Save serial to database"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    if user_id is None:
        user_id = message.from_user.id

    # Create serial (without file_id - episodes will have their own)
    serial = await create_movie(
        session,
        title=data["title"],
        channel_id=config.MOVIE_CHANNEL_ID,
        added_by=user_id,
        year=data.get("year", 2024),
        language=data.get("movie_language", "O'zbek"),
        quality=data.get("quality", "1080p"),
        category="Serial",
        thumbnail_url=data.get("poster_url"),
        thumbnail_file_id=data.get("thumbnail_file_id"),
        total_episodes=0,
        total_seasons=1
    )

    # Add genres
    for genre_id in data.get("selected_genres", []):
        await add_movie_genre(session, serial.id, genre_id)

    await state.clear()

    await message.answer(
        f"✅ <b>Serial qo'shildi!</b>\n\n"
        f"📺 {data['title']}\n"
        f"🆔 Kod: <code>{serial.id}</code>\n\n"
        f"Endi qismlarni qo'shish uchun:\n"
        f"/add_episode {serial.id}",
        parse_mode="HTML"
    )


# ==================== ADD EPISODE ====================

@router.message(Command("add_episode"))
async def cmd_add_episode(message: Message, state: FSMContext, session: AsyncSession):
    """Start adding episode to serial"""
    user = await get_user(session, message.from_user.id)
    lang = user.language if user else "uz"

    if not await check_admin(session, message.from_user.id):
        await message.answer(t("not_admin", lang))
        return

    # Check if serial ID provided
    parts = message.text.split()

    if len(parts) > 1:
        serial_id = parts[1]
        if serial_id.isdigit():
            serial = await get_movie(session, int(serial_id))
            if serial and serial.category in ["Serial", "Anime"]:
                await state.set_state(EpisodeAddState.waiting_season)
                await state.update_data(
                    lang=lang,
                    serial_id=serial.id,
                    serial_title=serial.title
                )

                await message.answer(
                    f"📺 <b>{serial.title}</b>\n\n"
                    f"Fasl raqamini kiriting (masalan: 1):",
                    parse_mode="HTML",
                    reply_markup=cancel_keyboard(lang)
                )
                return
            else:
                await message.answer("❌ Serial topilmadi yoki bu serial emas")
                return

    await state.set_state(EpisodeAddState.waiting_serial_id)
    await state.update_data(lang=lang)

    await message.answer(
        "🎬 <b>Qism qo'shish</b>\n\n"
        "Serial ID sini kiriting:",
        parse_mode="HTML",
        reply_markup=cancel_keyboard(lang)
    )


@router.message(EpisodeAddState.waiting_serial_id, F.text)
async def process_episode_serial_id(message: Message, state: FSMContext, session: AsyncSession):
    """Process serial ID"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    if not message.text.isdigit():
        await message.answer(t("invalid_input", lang))
        return

    serial_id = int(message.text)
    serial = await get_movie(session, serial_id)

    if not serial:
        await message.answer("❌ Serial topilmadi")
        return

    if serial.category not in ["Serial", "Anime"]:
        await message.answer("❌ Bu serial emas. Kategoriyasi: " + serial.category)
        return

    await state.update_data(serial_id=serial.id, serial_title=serial.title)
    await state.set_state(EpisodeAddState.waiting_season)

    await message.answer(
        f"📺 <b>{serial.title}</b>\n\n"
        f"Fasl raqamini kiriting (masalan: 1):",
        parse_mode="HTML"
    )


@router.message(EpisodeAddState.waiting_season, F.text)
async def process_episode_season(message: Message, state: FSMContext):
    """Process season number"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    if not message.text.isdigit():
        await message.answer("❌ Raqam kiriting")
        return

    season = int(message.text)

    if season < 1 or season > 50:
        await message.answer("❌ Fasl raqami 1-50 orasida bo'lishi kerak")
        return

    await state.update_data(season=season)
    await state.set_state(EpisodeAddState.waiting_episode_number)

    await message.answer(
        f"📁 {season}-fasl\n\n"
        f"Qism raqamini kiriting (masalan: 1):"
    )


@router.message(EpisodeAddState.waiting_episode_number, F.text)
async def process_episode_number(message: Message, state: FSMContext):
    """Process episode number"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    if not message.text.isdigit():
        await message.answer("❌ Raqam kiriting")
        return

    episode_num = int(message.text)

    if episode_num < 1 or episode_num > 500:
        await message.answer("❌ Qism raqami 1-500 orasida bo'lishi kerak")
        return

    await state.update_data(episode_number=episode_num)
    await state.set_state(EpisodeAddState.waiting_video)

    serial_title = data.get("serial_title", "Serial")
    season = data.get("season", 1)

    await message.answer(
        f"📺 {serial_title}\n"
        f"📁 {season}-fasl, {episode_num}-qism\n\n"
        f"Endi videoni yuboring yoki kanaldan forward qiling:"
    )


@router.message(EpisodeAddState.waiting_video, F.video | F.document | F.animation)
async def process_episode_video(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    """Process episode video"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    file_id = get_file_id_from_message(message)

    if not file_id:
        await message.answer("❌ Video topilmadi")
        return

    serial_id = data.get("serial_id")
    season = data.get("season", 1)
    episode_num = data.get("episode_number", 1)
    serial_title = data.get("serial_title", "Serial")

    # Forward to channel
    try:
        forwarded = await message.forward(config.MOVIE_CHANNEL_ID)
        message_id = forwarded.message_id
        channel_id = config.MOVIE_CHANNEL_ID
    except Exception as e:
        await message.answer(f"❌ Kanalga yuborishda xato: {e}")
        return

    # Create episode
    episode = await create_episode(
        session,
        movie_id=serial_id,
        episode_number=episode_num,
        season_number=season,
        file_id=file_id,
        message_id=message_id,
        channel_id=channel_id
    )

    # Update serial total_seasons if needed
    serial = await get_movie(session, serial_id)
    if serial and season > serial.total_seasons:
        await update_movie(session, serial_id, total_seasons=season)

    await state.set_state(EpisodeAddState.waiting_more)

    await message.answer(
        f"✅ <b>Qism qo'shildi!</b>\n\n"
        f"📺 {serial_title}\n"
        f"📁 {season}-fasl, {episode_num}-qism\n\n"
        f"Yana qism qo'shmoqchimisiz?",
        parse_mode="HTML",
        reply_markup=confirm_keyboard(lang)
    )


@router.message(EpisodeAddState.waiting_video, F.forward_from_chat)
async def process_episode_forward(message: Message, state: FSMContext, session: AsyncSession):
    """Process forwarded video from channel"""
    data = await state.get_data()
    lang = data.get("lang", "uz")

    # Check if it's a video
    file_id = get_file_id_from_message(message)

    if not file_id:
        await message.answer("❌ Video topilmadi")
        return

    serial_id = data.get("serial_id")
    season = data.get("season", 1)
    episode_num = data.get("episode_number", 1)
    serial_title = data.get("serial_title", "Serial")

    # Use original message info
    message_id = message.forward_from_message_id
    channel_id = message.forward_from_chat.id

    # Create episode
    episode = await create_episode(
        session,
        movie_id=serial_id,
        episode_number=episode_num,
        season_number=season,
        file_id=file_id,
        message_id=message_id,
        channel_id=channel_id
    )

    # Update serial total_seasons if needed
    serial = await get_movie(session, serial_id)
    if serial and season > serial.total_seasons:
        await update_movie(session, serial_id, total_seasons=season)

    await state.set_state(EpisodeAddState.waiting_more)

    await message.answer(
        f"✅ <b>Qism qo'shildi!</b>\n\n"
        f"📺 {serial_title}\n"
        f"📁 {season}-fasl, {episode_num}-qism\n\n"
        f"Yana qism qo'shmoqchimisiz?",
        parse_mode="HTML",
        reply_markup=confirm_keyboard(lang)
    )


@router.callback_query(F.data == "confirm", EpisodeAddState.waiting_more)
async def add_more_episodes(callback: CallbackQuery, state: FSMContext):
    """Add more episodes"""
    data = await state.get_data()
    lang = data.get("lang", "uz")
    season = data.get("season", 1)
    episode_num = data.get("episode_number", 1)

    # Increment episode number
    await state.update_data(episode_number=episode_num + 1)
    await state.set_state(EpisodeAddState.waiting_video)

    serial_title = data.get("serial_title", "Serial")

    await callback.message.edit_text(
        f"📺 {serial_title}\n"
        f"📁 {season}-fasl, {episode_num + 1}-qism\n\n"
        f"Videoni yuboring:"
    )
    await callback.answer()


@router.callback_query(F.data == "cancel", EpisodeAddState.waiting_more)
async def finish_adding_episodes(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Finish adding episodes"""
    data = await state.get_data()
    lang = data.get("lang", "uz")
    serial_id = data.get("serial_id")

    await state.clear()

    serial = await get_movie(session, serial_id)
    episodes = await get_episodes_by_movie(session, serial_id)

    await callback.message.edit_text(
        f"✅ <b>Tayyor!</b>\n\n"
        f"📺 {serial.title if serial else 'Serial'}\n"
        f"📋 Jami qismlar: {len(episodes)}\n"
        f"🆔 Kod: <code>{serial_id}</code>",
        parse_mode="HTML"
    )
    await callback.answer()


# ==================== CANCEL ====================

@router.callback_query(F.data == "cancel_add")
async def cancel_serial_add(callback: CallbackQuery, state: FSMContext):
    """Cancel adding"""
    current_state = await state.get_state()

    if current_state and (current_state.startswith("SerialAddState") or current_state.startswith("EpisodeAddState")):
        await state.clear()
        await callback.message.edit_text("❌ Bekor qilindi")

    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_episode_add(callback: CallbackQuery, state: FSMContext):
    """Cancel adding"""
    current_state = await state.get_state()

    if current_state:
        await state.clear()
        await callback.message.edit_text("❌ Bekor qilindi")

    await callback.answer()