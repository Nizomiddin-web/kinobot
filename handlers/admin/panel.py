"""
Admin handlers - Panel and Statistics
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from config import config
from database.crud import (
    get_user, is_admin, is_superadmin, get_statistics,
    get_top_users_by_watches, get_top_users_by_ratings,
    get_all_admins
)
from keyboards import admin_keyboard
from locales import t
from utils import format_number

router = Router()


async def check_admin(session: AsyncSession, user_id: int) -> bool:
    """Check if user is admin or superadmin"""
    if user_id in config.SUPER_ADMIN_IDS:
        return True
    return await is_admin(session, user_id)


@router.message(Command("admin"))
async def cmd_admin(message: Message, session: AsyncSession):
    """Handle /admin command"""
    user = await get_user(session, message.from_user.id)
    lang = user.language if user else "uz"
    
    if not await check_admin(session, message.from_user.id):
        await message.answer(t("not_admin", lang))
        return
    
    stats = await get_statistics(session)
    
    text = t(
        "admin_panel", lang,
        users=format_number(stats["users"]),
        today_users=format_number(stats["today_users"]),
        movies=format_number(stats["movies"]),
        views=format_number(stats["total_views"]),
        ratings=format_number(stats["total_ratings"])
    )
    
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=admin_keyboard(lang)
    )


@router.callback_query(F.data == "admin:panel")
async def show_admin_panel(callback: CallbackQuery, session: AsyncSession):
    """Show admin panel"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"
    
    if not await check_admin(session, callback.from_user.id):
        await callback.answer(t("not_admin", lang), show_alert=True)
        return
    
    stats = await get_statistics(session)
    
    text = t(
        "admin_panel", lang,
        users=format_number(stats["users"]),
        today_users=format_number(stats["today_users"]),
        movies=format_number(stats["movies"]),
        views=format_number(stats["total_views"]),
        ratings=format_number(stats["total_ratings"])
    )
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=admin_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data == "admin:stats")
async def show_stats(callback: CallbackQuery, session: AsyncSession):
    """Show detailed statistics"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"
    
    if not await check_admin(session, callback.from_user.id):
        await callback.answer(t("not_admin", lang), show_alert=True)
        return
    
    stats = await get_statistics(session)
    
    text = f"""📊 <b>Batafsil statistika</b>

👥 <b>Foydalanuvchilar:</b>
• Jami: {format_number(stats["users"])}
• Bugun: {format_number(stats["today_users"])}

🎬 <b>Kinolar:</b>
• Jami: {format_number(stats["movies"])}
• Ko'rishlar: {format_number(stats["total_views"])}

⭐ <b>Baholar:</b>
• Jami: {format_number(stats["total_ratings"])}
"""
    
    from keyboards import back_keyboard
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=back_keyboard("admin:panel", lang)
    )
    await callback.answer()


@router.callback_query(F.data == "admin:top_users")
async def show_top_users(callback: CallbackQuery, session: AsyncSession):
    """Show top users"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"
    
    if not await check_admin(session, callback.from_user.id):
        await callback.answer(t("not_admin", lang), show_alert=True)
        return
    
    # Top by watches
    top_watchers = await get_top_users_by_watches(session, limit=10)
    
    # Top by ratings
    top_raters = await get_top_users_by_ratings(session, limit=10)
    
    text = t("top_users", lang)
    
    text += "\n<b>🎬 Ko'p kino ko'rganlar:</b>\n"
    for i, (u, count) in enumerate(top_watchers, 1):
        name = u.full_name[:20] + "..." if len(u.full_name) > 20 else u.full_name
        text += f"{i}. {name} - {count} ta kino\n"
    
    text += "\n<b>⭐ Ko'p baho berganlar:</b>\n"
    for i, (u, count) in enumerate(top_raters, 1):
        name = u.full_name[:20] + "..." if len(u.full_name) > 20 else u.full_name
        text += f"{i}. {name} - {count} ta baho\n"
    
    from keyboards import back_keyboard
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=back_keyboard("admin:panel", lang)
    )
    await callback.answer()


@router.callback_query(F.data == "admin:admins")
async def show_admins(callback: CallbackQuery, session: AsyncSession):
    """Show admins list"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"
    
    if not await check_admin(session, callback.from_user.id):
        await callback.answer(t("not_admin", lang), show_alert=True)
        return
    
    admins = await get_all_admins(session)
    
    text = "👥 <b>Adminlar ro'yxati:</b>\n\n"
    
    # Add super admins from config
    text += "<b>Super adminlar:</b>\n"
    for admin_id in config.SUPER_ADMIN_IDS:
        text += f"• <code>{admin_id}</code> (config)\n"
    
    if admins:
        text += "\n<b>Bazadagi adminlar:</b>\n"
        for admin in admins:
            role_emoji = "👑" if admin.role == "superadmin" else "👤"
            text += f"• {role_emoji} <code>{admin.user_id}</code> ({admin.role})\n"
    
    from keyboards import back_keyboard
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=back_keyboard("admin:panel", lang)
    )
    await callback.answer()
