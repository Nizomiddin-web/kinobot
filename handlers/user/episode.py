"""
User handlers - Episode operations
"""

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import (
    get_user, get_or_create_user, get_movie, get_episode,
    get_episodes_by_movie, get_seasons_for_movie,
    increment_movie_views, add_to_history
)
from keyboards import episodes_keyboard, episode_keyboard, movie_keyboard
from locales import t

router = Router()


@router.callback_query(F.data.startswith("episodes:"))
async def show_episodes(callback: CallbackQuery, session: AsyncSession):
    """Show episodes list for a series"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"

    movie_id = int(callback.data.split(":")[1])
    movie = await get_movie(session, movie_id)

    if not movie:
        await callback.answer(t("movie_not_found", lang), show_alert=True)
        return

    # Get seasons
    seasons = await get_seasons_for_movie(session, movie_id)
    total_seasons = len(seasons) if seasons else 1
    current_season = seasons[0] if seasons else 1

    # Get episodes for first season
    episodes = await get_episodes_by_movie(session, movie_id, season=current_season)

    if not episodes:
        await callback.answer(
            "Qismlar hali qo'shilmagan" if lang == "uz" else "Серии еще не добавлены" if lang == "ru" else "Episodes not added yet",
            show_alert=True
        )
        return

    title = movie.get_title(lang)
    text = f"📺 <b>{title}</b>\n\n"

    if total_seasons > 1:
        text += f"📁 {current_season}-fasl | Jami: {len(episodes)} qism\n\n"
    else:
        text += f"📋 Jami: {len(episodes)} qism\n\n"

    text += "Qismni tanlang:" if lang == "uz" else "Выберите серию:" if lang == "ru" else "Select episode:"

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=episodes_keyboard(episodes, movie_id, lang, current_season, total_seasons)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("season:"))
async def change_season(callback: CallbackQuery, session: AsyncSession):
    """Change season"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"

    parts = callback.data.split(":")
    movie_id = int(parts[1])
    season = int(parts[2])

    movie = await get_movie(session, movie_id)

    if not movie:
        await callback.answer(t("movie_not_found", lang), show_alert=True)
        return

    # Get seasons
    seasons = await get_seasons_for_movie(session, movie_id)
    total_seasons = len(seasons) if seasons else 1

    # Get episodes for selected season
    episodes = await get_episodes_by_movie(session, movie_id, season=season)

    title = movie.get_title(lang)
    text = f"📺 <b>{title}</b>\n\n"
    text += f"📁 {season}-fasl | Jami: {len(episodes)} qism\n\n"
    text += "Qismni tanlang:" if lang == "uz" else "Выберите серию:" if lang == "ru" else "Select episode:"

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=episodes_keyboard(episodes, movie_id, lang, season, total_seasons)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ep:"))
async def send_episode(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    """Send single episode"""
    user, _ = await get_or_create_user(
        session,
        user_id=callback.from_user.id,
        full_name=callback.from_user.full_name,
        username=callback.from_user.username
    )
    lang = user.language if user else "uz"

    episode_id = int(callback.data.split(":")[1])
    episode = await get_episode(session, episode_id)

    if not episode:
        await callback.answer(
            "Qism topilmadi" if lang == "uz" else "Серия не найдена" if lang == "ru" else "Episode not found",
            show_alert=True
        )
        return

    movie = await get_movie(session, episode.movie_id)
    title = movie.get_title(lang) if movie else "Serial"

    # Increment views
    if movie:
        await increment_movie_views(session, movie.id)
        # await add_to_history(session, callback.from_user.id, movie.id)

    # Send episode info
    ep_title = episode.title or f"{episode.episode_number}-qism"
    text = f"📺 <b>{title}</b>\n"
    text += f"🎬 {episode.season_number}-fasl, {episode.episode_number}-qism"
    if episode.title:
        text += f"\n📝 {episode.title}"

    # Send video
    try:
        await callback.message.answer_video(
                video=episode.file_id,
                caption=text
            )
    except:
        await callback.answer(t("error_occurred", lang), show_alert=True)

    await callback.answer()


@router.callback_query(F.data.startswith("all_eps:"))
async def send_all_episodes(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    """Send all episodes of a season"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"

    parts = callback.data.split(":")
    movie_id = int(parts[1])
    season = int(parts[2])

    movie = await get_movie(session, movie_id)

    if not movie:
        await callback.answer(t("movie_not_found", lang), show_alert=True)
        return

    episodes = await get_episodes_by_movie(session, movie_id, season=season)

    if not episodes:
        await callback.answer("Qismlar topilmadi", show_alert=True)
        return

    # Confirm sending all
    await callback.answer(
        f"{len(episodes)} ta qism yuborilmoqda..." if lang == "uz" else f"Отправляется {len(episodes)} серий...",
        show_alert=True
    )

    title = movie.get_title(lang)

    # Increment views
    await increment_movie_views(session, movie.id)
    await add_to_history(session, callback.from_user.id, movie.id)

    # Send episodes one by one
    sent = 0
    for episode in episodes:
        try:
            await bot.copy_message(
                chat_id=callback.message.chat.id,
                from_chat_id=episode.channel_id,
                message_id=episode.message_id
            )
            sent += 1

            # Rate limiting - avoid flood
            if sent % 5 == 0:
                import asyncio
                await asyncio.sleep(1)

        except Exception:
            try:
                await callback.message.answer_video(
                    video=episode.file_id,
                    caption=f"{title} - {episode.season_number}x{episode.episode_number}"
                )
                sent += 1
            except:
                pass

    # Final message
    await callback.message.answer(
        f"✅ {sent}/{len(episodes)} qism yuborildi" if lang == "uz" else f"✅ Отправлено {sent}/{len(episodes)} серий"
    )