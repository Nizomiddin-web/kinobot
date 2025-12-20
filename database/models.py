"""
Database Models
All SQLAlchemy models for Kino Bot
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    BigInteger, Integer, String, Text, Float, Boolean, 
    DateTime, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    language: Mapped[str] = mapped_column(String(2), default="uz")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    ratings: Mapped[List["Rating"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    favorites: Mapped[List["Favorite"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    watch_history: Mapped[List["WatchHistory"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.user_id}: {self.full_name}>"


class Movie(Base):
    """Movie model"""
    __tablename__ = "movies"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title_uz: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_ru: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title_en: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    file_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Nullable for series
    thumbnail_file_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    message_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Nullable for series
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    year: Mapped[int] = mapped_column(Integer, default=2024)
    language: Mapped[str] = mapped_column(String(50), default="O'zbek")
    quality: Mapped[str] = mapped_column(String(10), default="1080p")
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    category: Mapped[str] = mapped_column(String(20), default="Kino")  # Kino, Serial, Anime, Multfilm

    # Serial specific
    total_episodes: Mapped[int] = mapped_column(Integer, default=0)  # Jami qismlar soni
    total_seasons: Mapped[int] = mapped_column(Integer, default=1)  # Jami fasllar soni

    user_rating: Mapped[float] = mapped_column(Float, default=0.0)
    rating_count: Mapped[int] = mapped_column(Integer, default=0)
    views: Mapped[int] = mapped_column(Integer, default=0)

    added_by: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    genres: Mapped[List["MovieGenre"]] = relationship(back_populates="movie", cascade="all, delete-orphan")
    ratings: Mapped[List["Rating"]] = relationship(back_populates="movie", cascade="all, delete-orphan")
    favorites: Mapped[List["Favorite"]] = relationship(back_populates="movie", cascade="all, delete-orphan")
    watch_history: Mapped[List["WatchHistory"]] = relationship(back_populates="movie", cascade="all, delete-orphan")
    episodes: Mapped[List["Episode"]] = relationship(back_populates="movie", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_movie_search', 'title', 'title_uz', 'title_ru'),
        Index('idx_movie_category', 'category'),
        Index('idx_movie_year', 'year'),
    )

    def __repr__(self):
        return f"<Movie {self.id}: {self.title}>"

    @property
    def rating_display(self) -> str:
        """Display rating with stars"""
        if self.rating_count == 0:
            return "⭐ --"
        return f"⭐ {self.user_rating:.1f}"

    @property
    def is_series(self) -> bool:
        """Check if this is a series"""
        return self.category in ["Serial", "Anime", "Multfilm"] and self.total_episodes > 0

    def get_title(self, lang: str = "uz") -> str:
        """Get title in specified language"""
        if lang == "ru" and self.title_ru:
            return self.title_ru
        elif lang == "en" and self.title_en:
            return self.title_en
        elif lang == "uz" and self.title_uz:
            return self.title_uz
        return self.title


class Episode(Base):
    """Serial episodes"""
    __tablename__ = "episodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    movie_id: Mapped[int] = mapped_column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)
    episode_number: Mapped[int] = mapped_column(Integer, nullable=False)  # 1, 2, 3...
    season_number: Mapped[int] = mapped_column(Integer, default=1)  # Fasl raqami
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Qism nomi (ixtiyoriy)

    file_id: Mapped[str] = mapped_column(String(255), nullable=False)
    message_id: Mapped[int] = mapped_column(Integer, nullable=False)
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    movie: Mapped["Movie"] = relationship(back_populates="episodes")

    __table_args__ = (
        UniqueConstraint('movie_id', 'season_number', 'episode_number', name='unique_episode'),
        Index('idx_episode_movie', 'movie_id'),
    )

    def __repr__(self):
        return f"<Episode {self.movie_id} S{self.season_number}E{self.episode_number}>"


class Genre(Base):
    """Genre model"""
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name_uz: Mapped[str] = mapped_column(String(50), nullable=False)
    name_ru: Mapped[str] = mapped_column(String(50), nullable=False)
    name_en: Mapped[str] = mapped_column(String(50), nullable=False)

    # Relationships
    movies: Mapped[List["MovieGenre"]] = relationship(back_populates="genre", cascade="all, delete-orphan")

    def get_name(self, lang: str = "uz") -> str:
        """Get genre name in specified language"""
        if lang == "ru":
            return self.name_ru
        elif lang == "en":
            return self.name_en
        return self.name_uz

    def __repr__(self):
        return f"<Genre {self.name}>"


class MovieGenre(Base):
    """Movie-Genre relationship"""
    __tablename__ = "movie_genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    movie_id: Mapped[int] = mapped_column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    genre_id: Mapped[int] = mapped_column(Integer, ForeignKey("genres.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    movie: Mapped["Movie"] = relationship(back_populates="genres")
    genre: Mapped["Genre"] = relationship(back_populates="movies")

    __table_args__ = (
        UniqueConstraint('movie_id', 'genre_id', name='unique_movie_genre'),
    )


class Rating(Base):
    """User rating for movie"""
    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    movie_id: Mapped[int] = mapped_column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="ratings")
    movie: Mapped["Movie"] = relationship(back_populates="ratings")

    __table_args__ = (
        UniqueConstraint('user_id', 'movie_id', name='unique_user_movie_rating'),
    )


class Favorite(Base):
    """User favorites"""
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    movie_id: Mapped[int] = mapped_column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="favorites")
    movie: Mapped["Movie"] = relationship(back_populates="favorites")

    __table_args__ = (
        UniqueConstraint('user_id', 'movie_id', name='unique_user_favorite'),
    )


class WatchHistory(Base):
    """User watch history"""
    __tablename__ = "watch_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    movie_id: Mapped[int] = mapped_column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    watched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="watch_history")
    movie: Mapped["Movie"] = relationship(back_populates="watch_history")

    __table_args__ = (
        Index('idx_watch_history_user', 'user_id'),
        Index('idx_watch_history_time', 'watched_at'),
    )


class Channel(Base):
    """Subscription channels"""
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    channel_username: Mapped[str] = mapped_column(String(255), nullable=False)
    channel_title: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Channel {self.channel_username}>"


class Admin(Base):
    """Bot admins"""
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="admin")  # superadmin, admin
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Admin {self.user_id}: {self.role}>"