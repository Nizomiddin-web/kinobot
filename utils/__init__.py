"""
Utility functions
"""

import re
from typing import Optional, Tuple, List, Dict
from aiogram import Bot
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

from config import config


async def check_subscription(bot: Bot, user_id: int, channels: list) -> Tuple[bool, List]:
    """
    Check if user is subscribed to all channels
    Returns: (is_subscribed, not_subscribed_channels)
    """
    not_subscribed = []
    
    for channel in channels:
        try:
            member = await bot.get_chat_member(channel.channel_id, user_id)
            if member.status in ['left', 'kicked']:
                not_subscribed.append(channel)
        except TelegramBadRequest:
            # Bot is not admin in channel or channel doesn't exist
            continue
    
    return len(not_subscribed) == 0, not_subscribed


def parse_movie_caption(caption: str) -> Dict:
    """
    Parse movie info from caption
    Format: Title | Year | Genre1, Genre2 | Language | Quality | Duration min
    
    Example: Avatar 2 | 2022 | Fantasy, Action | O'zbek | 1080p | 192 min
    """
    result = {
        "title": "",
        "year": 2024,
        "genres": [],
        "language": "O'zbek",
        "quality": "1080p",
        "duration": None,
        "caption": ""
    }
    
    if not caption:
        return result
    
    # Split by newlines - first line is metadata, rest is description
    lines = caption.strip().split('\n')
    metadata_line = lines[0]
    
    # Check if first line contains | separator (metadata format)
    if '|' in metadata_line:
        parts = [p.strip() for p in metadata_line.split('|')]
        
        # Title (required)
        if len(parts) >= 1 and parts[0]:
            result["title"] = parts[0]
        
        # Year
        if len(parts) >= 2:
            year_match = re.search(r'\d{4}', parts[1])
            if year_match:
                result["year"] = int(year_match.group())
        
        # Genres
        if len(parts) >= 3:
            genres = [g.strip().lower() for g in parts[2].split(',')]
            result["genres"] = genres
        
        # Language
        if len(parts) >= 4:
            result["language"] = parts[3]
        
        # Quality
        if len(parts) >= 5:
            quality_match = re.search(r'(360p|480p|720p|1080p|4K)', parts[4], re.IGNORECASE)
            if quality_match:
                result["quality"] = quality_match.group()
        
        # Duration
        if len(parts) >= 6:
            duration_match = re.search(r'(\d+)\s*min', parts[5], re.IGNORECASE)
            if duration_match:
                result["duration"] = int(duration_match.group(1))
        
        # Rest is caption
        if len(lines) > 1:
            result["caption"] = '\n'.join(lines[1:]).strip()
    else:
        # No metadata format - treat entire caption as title or description
        result["caption"] = caption
    
    return result


def detect_category_from_genres(genres: List[str]) -> str:
    """Detect category from genres"""
    genres_lower = [g.lower() for g in genres]
    
    if 'anime' in genres_lower or 'yapon' in genres_lower:
        return "Anime"
    elif 'animation' in genres_lower or 'animatsiya' in genres_lower or 'multfilm' in genres_lower:
        return "Multfilm"
    elif 'serial' in genres_lower:
        return "Serial"
    
    return "Kino"


def format_movie_list(movies: list, lang: str = "uz") -> str:
    """Format movies list for display"""
    text = ""
    for i, movie in enumerate(movies, 1):
        title = movie.get_title(lang)
        if len(title) > 40:
            title = title[:37] + "..."
        
        text += f"{i}. <b>{title}</b> ({movie.year}) {movie.rating_display}\n"
        text += f"   🆔 <code>{movie.id}</code>\n\n"
    
    return text


def format_duration(minutes: Optional[int]) -> str:
    """Format duration in human readable format"""
    if not minutes:
        return "—"
    
    if minutes < 60:
        return f"{minutes} min"
    
    hours = minutes // 60
    mins = minutes % 60
    
    if mins == 0:
        return f"{hours} soat"
    
    return f"{hours} soat {mins} min"


def format_number(num: int) -> str:
    """Format number with thousands separator"""
    return f"{num:,}".replace(",", " ")


def is_valid_movie_id(text: str) -> bool:
    """Check if text is valid movie ID"""
    return text.isdigit() and 1 <= int(text) <= 999999


def extract_movie_id(text: str) -> Optional[int]:
    """Extract movie ID from text"""
    # Direct number
    if text.isdigit():
        return int(text)
    
    # With prefix like "id123" or "#123"
    match = re.search(r'(?:id|#)?(\d+)', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    return None


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def escape_html(text: str) -> str:
    """Escape HTML special characters"""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def get_file_id_from_message(message: Message) -> Optional[str]:
    """Extract file_id from message"""
    if message.video:
        return message.video.file_id
    elif message.document:
        return message.document.file_id
    elif message.animation:
        return message.animation.file_id
    return None


def get_thumbnail_from_message(message: Message) -> Optional[str]:
    """Extract thumbnail file_id from message"""
    if message.video and message.video.thumbnail:
        return message.video.thumbnail.file_id
    elif message.document and message.document.thumbnail:
        return message.document.thumbnail.file_id
    elif message.animation and message.animation.thumbnail:
        return message.animation.thumbnail.file_id
    return None


def validate_year(text: str) -> Optional[int]:
    """Validate year input"""
    try:
        year = int(text)
        if 1900 <= year <= 2100:
            return year
    except ValueError:
        pass
    return None


def validate_duration(text: str) -> Optional[int]:
    """Validate duration input"""
    try:
        # Extract number from text like "120 min" or just "120"
        match = re.search(r'(\d+)', text)
        if match:
            duration = int(match.group(1))
            if 1 <= duration <= 1000:
                return duration
    except ValueError:
        pass
    return None


async def safe_delete_message(message: Message) -> bool:
    """Safely delete message"""
    try:
        await message.delete()
        return True
    except TelegramBadRequest:
        return False


def get_rating_stars(rating: float) -> str:
    """Convert rating to stars display"""
    full_stars = int(rating)
    half_star = rating - full_stars >= 0.5
    empty_stars = 5 - full_stars - (1 if half_star else 0)

    stars = "⭐" * full_stars
    if half_star:
        stars += "✨"
    stars += "☆" * empty_stars

    return stars