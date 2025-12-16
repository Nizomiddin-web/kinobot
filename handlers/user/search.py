"""
User handlers - Search functionality
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.crud import get_user, search_movies
from keyboards import movies_list_keyboard, cancel_keyboard
from locales import t
from states import SearchState
from utils import format_movie_list

router = Router()


@router.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext, session: AsyncSession):
    """Handle /search command"""
    user = await get_user(session, message.from_user.id)
    lang = user.language if user else "uz"
    
    await state.set_state(SearchState.waiting_query)
    await message.answer(
        t("search_prompt", lang),
        reply_markup=cancel_keyboard(lang)
    )


@router.message(SearchState.waiting_query)
async def process_search_query(message: Message, state: FSMContext, session: AsyncSession):
    """Process search query"""
    user = await get_user(session, message.from_user.id)
    lang = user.language if user else "uz"
    
    query = message.text.strip()
    
    if not query or len(query) < 2:
        await message.answer(t("invalid_input", lang))
        return
    
    # Search movies
    movies = await search_movies(session, query)
    
    await state.clear()
    
    if not movies:
        await message.answer(t("search_no_results", lang, query=query))
        return
    
    # Show results
    text = t("search_results", lang, query=query, count=len(movies))
    text += "\n" + format_movie_list(movies[:10], lang)
    
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=movies_list_keyboard(movies[:10], lang) if len(movies) > 0 else None
    )


@router.callback_query(F.data == "cancel", SearchState.waiting_query)
async def cancel_search(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Cancel search"""
    user = await get_user(session, callback.from_user.id)
    lang = user.language if user else "uz"
    
    await state.clear()
    await callback.message.edit_text(t("search_cancelled", lang))
    await callback.answer()


# Quick search with /search query format
@router.message(Command("search"))
async def cmd_search_with_query(message: Message, session: AsyncSession):
    """Handle /search query command"""
    user = await get_user(session, message.from_user.id)
    lang = user.language if user else "uz"
    
    # Extract query from command
    parts = message.text.split(maxsplit=1)
    
    if len(parts) < 2:
        # No query provided, ask for it
        return
    
    query = parts[1].strip()
    
    if len(query) < 2:
        await message.answer(t("invalid_input", lang))
        return
    
    # Search movies
    movies = await search_movies(session, query)
    
    if not movies:
        await message.answer(t("search_no_results", lang, query=query))
        return
    
    # Show results
    text = t("search_results", lang, query=query, count=len(movies))
    text += "\n" + format_movie_list(movies[:10], lang)
    
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=movies_list_keyboard(movies[:10], lang) if len(movies) > 0 else None
    )
