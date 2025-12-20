"""
FSM States for bot
"""

from aiogram.fsm.state import State, StatesGroup


class SearchState(StatesGroup):
    """Search states"""
    waiting_query = State()


class MovieAddState(StatesGroup):
    """States for adding movie"""
    waiting_video = State()
    waiting_title = State()
    waiting_year = State()
    waiting_language = State()
    waiting_quality = State()
    waiting_category = State()
    waiting_genres = State()
    waiting_duration = State()
    waiting_poster = State()
    confirming = State()



class MovieEditState(StatesGroup):
    """States for editing movie"""
    selecting_field = State()
    waiting_value = State()


class ChannelAddState(StatesGroup):
    """States for adding channel"""
    waiting_forward = State()


class BroadcastState(StatesGroup):
    """States for broadcast"""
    waiting_message = State()
    confirming = State()


class AdminAddState(StatesGroup):
    """States for adding admin"""
    waiting_user_id = State()
