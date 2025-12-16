"""
Admin handlers - Broadcast messages
"""

import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import get_user, get_all_users, get_users_count
from keyboards import confirm_keyboard, cancel_keyboard, back_keyboard
from locales import t
from states import BroadcastState
from handlers.admin.panel import check_admin

router = Router()


@router.callback_query(F.data == "admin:broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Start broadcast process"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"
    
    if not await check_admin(session, callback.from_user.id):
        await callback.answer(t("not_admin", lang), show_alert=True)
        return
    
    await state.set_state(BroadcastState.waiting_message)
    await state.update_data(lang=lang)
    
    await callback.message.edit_text(
        t("broadcast_prompt", lang),
        reply_markup=cancel_keyboard(lang)
    )
    await callback.answer()


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext, session: AsyncSession):
    """Broadcast command"""
    user = await get_user(session, message.from_user.id)
    lang = user.language if user else "uz"
    
    if not await check_admin(session, message.from_user.id):
        await message.answer(t("not_admin", lang))
        return
    
    await state.set_state(BroadcastState.waiting_message)
    await state.update_data(lang=lang)
    
    await message.answer(
        t("broadcast_prompt", lang),
        reply_markup=cancel_keyboard(lang)
    )


@router.message(BroadcastState.waiting_message)
async def process_broadcast_message(message: Message, state: FSMContext, session: AsyncSession):
    """Process broadcast message"""
    data = await state.get_data()
    lang = data.get("lang", "uz")
    
    # Store message info for forwarding
    await state.update_data(
        broadcast_chat_id=message.chat.id,
        broadcast_message_id=message.message_id
    )
    
    await state.set_state(BroadcastState.confirming)
    
    # Get users count
    count = await get_users_count(session)
    
    await message.answer(
        t("broadcast_confirm", lang, count=count),
        reply_markup=confirm_keyboard(lang)
    )


@router.callback_query(F.data == "confirm", BroadcastState.confirming)
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot):
    """Confirm and execute broadcast"""
    data = await state.get_data()
    lang = data.get("lang", "uz")
    
    chat_id = data.get("broadcast_chat_id")
    message_id = data.get("broadcast_message_id")
    
    await state.clear()
    
    await callback.message.edit_text(t("broadcast_started", lang))
    
    # Get all users
    users = await get_all_users(session)
    
    success = 0
    failed = 0
    
    for user in users:
        try:
            await bot.copy_message(
                chat_id=user.user_id,
                from_chat_id=chat_id,
                message_id=message_id
            )
            success += 1
            
            # Rate limiting - 30 messages per second
            if success % 30 == 0:
                await asyncio.sleep(1)
                
        except TelegramForbiddenError:
            # User blocked the bot
            failed += 1
        except TelegramBadRequest:
            failed += 1
        except Exception:
            failed += 1
    
    await callback.message.answer(
        t("broadcast_done", lang, success=success, failed=failed),
        reply_markup=back_keyboard("admin:panel", lang)
    )
    await callback.answer()


@router.callback_query(F.data == "cancel", BroadcastState.confirming)
async def cancel_broadcast_confirm(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Cancel broadcast at confirmation"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"
    
    await state.clear()
    
    await callback.message.edit_text(
        "❌ Xabar yuborish bekor qilindi",
        reply_markup=back_keyboard("admin:panel", lang)
    )
    await callback.answer()


@router.callback_query(F.data == "cancel", BroadcastState.waiting_message)
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Cancel broadcast"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"
    
    await state.clear()
    
    await callback.message.edit_text(
        "❌ Xabar yuborish bekor qilindi",
        reply_markup=back_keyboard("admin:panel", lang)
    )
    await callback.answer()
