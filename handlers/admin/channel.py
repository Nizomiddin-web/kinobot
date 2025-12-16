"""
Admin handlers - Channel management
"""

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import (
    get_user, get_active_channels, add_channel, remove_channel,
    get_channel, toggle_channel
)
from keyboards import channels_admin_keyboard, cancel_keyboard, back_keyboard
from locales import t
from states import ChannelAddState
from handlers.admin.panel import check_admin

router = Router()


@router.callback_query(F.data == "admin:channels")
async def show_channels(callback: CallbackQuery, session: AsyncSession):
    """Show channels management"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"
    
    if not await check_admin(session, callback.from_user.id):
        await callback.answer(t("not_admin", lang), show_alert=True)
        return
    
    channels = await get_active_channels(session)
    
    # Get all channels (including inactive)
    from sqlalchemy import select
    from database.models import Channel
    from database import async_session
    
    async with async_session() as sess:
        result = await sess.execute(select(Channel))
        all_channels = list(result.scalars().all())
    
    text = t("channels_list", lang)
    
    if all_channels:
        for ch in all_channels:
            status = "✅" if ch.is_active else "❌"
            text += f"{status} @{ch.channel_username} - {ch.channel_title}\n"
    else:
        text += t("no_channels", lang)
    
    await callback.message.edit_text(
        text,
        reply_markup=channels_admin_keyboard(all_channels, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ch_toggle:"))
async def toggle_channel_status(callback: CallbackQuery, session: AsyncSession):
    """Toggle channel active status"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"
    
    if not await check_admin(session, callback.from_user.id):
        await callback.answer(t("not_admin", lang), show_alert=True)
        return
    
    channel_id = int(callback.data.split(":")[1])
    
    await toggle_channel(session, channel_id)
    
    # Refresh channels list
    from sqlalchemy import select
    from database.models import Channel
    from database import async_session
    
    async with async_session() as sess:
        result = await sess.execute(select(Channel))
        all_channels = list(result.scalars().all())
    
    text = t("channels_list", lang)
    
    if all_channels:
        for ch in all_channels:
            status = "✅" if ch.is_active else "❌"
            text += f"{status} @{ch.channel_username} - {ch.channel_title}\n"
    else:
        text += t("no_channels", lang)
    
    await callback.message.edit_text(
        text,
        reply_markup=channels_admin_keyboard(all_channels, lang)
    )
    await callback.answer("Status o'zgartirildi!")


@router.callback_query(F.data == "ch_add")
async def start_add_channel(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Start adding channel"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"
    
    if not await check_admin(session, callback.from_user.id):
        await callback.answer(t("not_admin", lang), show_alert=True)
        return
    
    await state.set_state(ChannelAddState.waiting_forward)
    await state.update_data(lang=lang)
    
    await callback.message.edit_text(
        t("forward_channel_msg", lang),
        reply_markup=cancel_keyboard(lang)
    )
    await callback.answer()


@router.message(ChannelAddState.waiting_forward, F.forward_from_chat)
async def process_channel_forward(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    """Process forwarded message from channel"""
    data = await state.get_data()
    lang = data.get("lang", "uz")
    
    chat = message.forward_from_chat
    
    if chat.type != "channel":
        await message.answer("❌ Bu kanal emas!")
        return
    
    # Check if bot is admin in channel
    try:
        bot_member = await bot.get_chat_member(chat.id, bot.id)
        if bot_member.status not in ["administrator", "creator"]:
            await message.answer(
                "❌ Bot bu kanalda admin emas!\n"
                "Avval botni kanalga admin qiling."
            )
            return
    except Exception as e:
        await message.answer(f"❌ Kanalni tekshirishda xato: {e}")
        return
    
    # Check if channel already exists
    existing = await get_channel(session, chat.id)
    if existing:
        await message.answer("⚠️ Bu kanal allaqachon qo'shilgan!")
        await state.clear()
        return
    
    # Add channel
    channel = await add_channel(
        session,
        channel_id=chat.id,
        channel_username=chat.username or str(chat.id),
        channel_title=chat.title
    )
    
    await state.clear()
    
    await message.answer(
        t("channel_added", lang, title=chat.title),
        reply_markup=back_keyboard("admin:channels", lang)
    )


@router.callback_query(F.data == "cancel", ChannelAddState.waiting_forward)
async def cancel_add_channel(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Cancel adding channel"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"
    
    await state.clear()
    
    await callback.message.edit_text(
        "❌ Bekor qilindi",
        reply_markup=back_keyboard("admin:channels", lang)
    )
    await callback.answer()


@router.message(Command("add_channel"))
async def cmd_add_channel(message: Message, state: FSMContext, session: AsyncSession):
    """Add channel command"""
    user = await get_user(session, message.from_user.id)
    lang = user.language if user else "uz"
    
    if not await check_admin(session, message.from_user.id):
        await message.answer(t("not_admin", lang))
        return
    
    await state.set_state(ChannelAddState.waiting_forward)
    await state.update_data(lang=lang)
    
    await message.answer(
        t("forward_channel_msg", lang),
        reply_markup=cancel_keyboard(lang)
    )


@router.message(Command("channels"))
async def cmd_channels(message: Message, session: AsyncSession):
    """Show channels command"""
    user = await get_user(session, message.from_user.id)
    lang = user.language if user else "uz"
    
    if not await check_admin(session, message.from_user.id):
        await message.answer(t("not_admin", lang))
        return
    
    from sqlalchemy import select
    from database.models import Channel
    from database import async_session
    
    async with async_session() as sess:
        result = await sess.execute(select(Channel))
        all_channels = list(result.scalars().all())
    
    text = t("channels_list", lang)
    
    if all_channels:
        for ch in all_channels:
            status = "✅" if ch.is_active else "❌"
            text += f"{status} @{ch.channel_username} - {ch.channel_title}\n"
    else:
        text += t("no_channels", lang)
    
    await message.answer(
        text,
        reply_markup=channels_admin_keyboard(all_channels, lang)
    )
