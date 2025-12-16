"""
Kino Bot Configuration
Supports PostgreSQL (local) and MySQL (server)
"""

from dataclasses import dataclass, field
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Bot configuration"""
    
    # Bot settings
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    # Database
    DATABASE_TYPE: str = os.getenv("DATABASE_TYPE", "postgresql")  # postgresql or mysql
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Channels
    MOVIE_CHANNEL_ID: int = int(os.getenv("MOVIE_CHANNEL_ID", "0"))
    
    # Admins
    SUPER_ADMIN_IDS: List[int] = field(default_factory=lambda: [
        int(x) for x in os.getenv("SUPER_ADMIN_IDS", "").split(",") if x
    ])
    
    # Settings
    MOVIES_PER_PAGE: int = 10
    SEARCH_LIMIT: int = 50
    INLINE_CACHE_TIME: int = 300
    
    # Movie add mode: caption, inline, minimal, auto
    DEFAULT_ADD_MODE: str = "auto"
    
    # Supported values
    LANGUAGES: List[str] = field(default_factory=lambda: [
        "O'zbek", "Rus", "Ingliz", "Koreys", "Turk", "Hind", "Yapon"
    ])
    
    QUALITIES: List[str] = field(default_factory=lambda: [
        "360p", "480p", "720p", "1080p", "4K"
    ])
    
    CATEGORIES: List[str] = field(default_factory=lambda: [
        "Kino", "Serial", "Anime", "Multfilm"
    ])
    
    @property
    def database_url(self) -> str:
        """Get async database URL"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        if self.DATABASE_TYPE == "postgresql":
            return "postgresql+asyncpg://postgres:postgres@localhost:5432/kino_bot"
        else:
            return "mysql+aiomysql://root:root@localhost:3306/kino_bot"


# Create config instance
config = Config()


# Bot interface languages
INTERFACE_LANGUAGES = {
    "uz": "🇺🇿 O'zbekcha",
    "ru": "🇷🇺 Русский", 
    "en": "🇬🇧 English"
}

# Default genres
DEFAULT_GENRES = [
    {"name": "action", "name_uz": "Jangari", "name_ru": "Боевик", "name_en": "Action"},
    {"name": "comedy", "name_uz": "Komediya", "name_ru": "Комедия", "name_en": "Comedy"},
    {"name": "drama", "name_uz": "Drama", "name_ru": "Драма", "name_en": "Drama"},
    {"name": "horror", "name_uz": "Qo'rqinchli", "name_ru": "Ужасы", "name_en": "Horror"},
    {"name": "thriller", "name_uz": "Triller", "name_ru": "Триллер", "name_en": "Thriller"},
    {"name": "romance", "name_uz": "Romantik", "name_ru": "Романтика", "name_en": "Romance"},
    {"name": "scifi", "name_uz": "Fantastika", "name_ru": "Фантастика", "name_en": "Sci-Fi"},
    {"name": "fantasy", "name_uz": "Fantazi", "name_ru": "Фэнтези", "name_en": "Fantasy"},
    {"name": "animation", "name_uz": "Animatsiya", "name_ru": "Анимация", "name_en": "Animation"},
    {"name": "documentary", "name_uz": "Hujjatli", "name_ru": "Документальный", "name_en": "Documentary"},
    {"name": "crime", "name_uz": "Jinoyat", "name_ru": "Криминал", "name_en": "Crime"},
    {"name": "adventure", "name_uz": "Sarguzasht", "name_ru": "Приключения", "name_en": "Adventure"},
    {"name": "family", "name_uz": "Oilaviy", "name_ru": "Семейный", "name_en": "Family"},
    {"name": "history", "name_uz": "Tarixiy", "name_ru": "Исторический", "name_en": "History"},
    {"name": "war", "name_uz": "Urush", "name_ru": "Военный", "name_en": "War"},
    {"name": "music", "name_uz": "Musiqiy", "name_ru": "Музыкальный", "name_en": "Musical"},
    {"name": "sport", "name_uz": "Sport", "name_ru": "Спортивный", "name_en": "Sport"},
]
