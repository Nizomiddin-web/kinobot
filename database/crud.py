"""
CRUD Operations
Database operations for all models
"""

from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy import select, func, update, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import (
    User, Movie, Genre, MovieGenre, Rating,
    Favorite, WatchHistory, Channel, Admin, Episode
)


# ==================== USER OPERATIONS ====================

async def get_user(session: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by telegram ID"""
    result = await session.execute(
        select(User).where(User.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    user_id: int,
    full_name: str,
    username: Optional[str] = None,
    language: str = "uz"
) -> User:
    """Create new user"""
    user = User(
        user_id=user_id,
        full_name=full_name,
        username=username,
        language=language
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_or_create_user(
    session: AsyncSession,
    user_id: int,
    full_name: str,
    username: Optional[str] = None
) -> Tuple[User, bool]:
    """Get existing user or create new one"""
    user = await get_user(session, user_id)
    if user:
        user.full_name = full_name
        user.username = username
        await session.commit()
        return user, False

    user = await create_user(session, user_id, full_name, username)
    return user, True


async def update_user_language(session: AsyncSession, user_id: int, language: str) -> bool:
    """Update user language"""
    result = await session.execute(
        update(User).where(User.user_id == user_id).values(language=language)
    )
    await session.commit()
    return result.rowcount > 0


async def get_users_count(session: AsyncSession) -> int:
    """Get total users count"""
    result = await session.execute(select(func.count(User.id)))
    return result.scalar() or 0


async def get_today_users_count(session: AsyncSession) -> int:
    """Get today's new users count"""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    result = await session.execute(
        select(func.count(User.id)).where(User.created_at >= today)
    )
    return result.scalar() or 0


async def get_all_users(session: AsyncSession, limit: int = 1000, offset: int = 0) -> List[User]:
    """Get all users for broadcast"""
    result = await session.execute(
        select(User)
        .where(User.is_banned == False)
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def ban_user(session: AsyncSession, user_id: int, ban: bool = True) -> bool:
    """Ban or unban user"""
    result = await session.execute(
        update(User).where(User.user_id == user_id).values(is_banned=ban)
    )
    await session.commit()
    return result.rowcount > 0


# ==================== MOVIE OPERATIONS ====================

async def get_movie(session: AsyncSession, movie_id: int) -> Optional[Movie]:
    """Get movie by ID"""
    result = await session.execute(
        select(Movie)
        .options(selectinload(Movie.genres).selectinload(MovieGenre.genre))
        .options(selectinload(Movie.episodes))
        .where(Movie.id == movie_id, Movie.is_active == True)
    )
    return result.scalar_one_or_none()


async def create_movie(
    session: AsyncSession,
    title: str,
    channel_id: int,
    added_by: int,
    **kwargs
) -> Movie:
    """Create new movie"""
    movie = Movie(
        title=title,
        channel_id=channel_id,
        added_by=added_by,
        **kwargs
    )
    session.add(movie)
    await session.commit()
    await session.refresh(movie)
    return movie


async def update_movie(session: AsyncSession, movie_id: int, **kwargs) -> bool:
    """Update movie data"""
    result = await session.execute(
        update(Movie).where(Movie.id == movie_id).values(**kwargs)
    )
    await session.commit()
    return result.rowcount > 0


async def delete_movie(session: AsyncSession, movie_id: int) -> bool:
    """Soft delete movie"""
    return await update_movie(session, movie_id, is_active=False)


async def increment_movie_views(session: AsyncSession, movie_id: int) -> None:
    """Increment movie views count"""
    await session.execute(
        update(Movie).where(Movie.id == movie_id).values(views=Movie.views + 1)
    )
    await session.commit()


async def search_movies(
    session: AsyncSession,
    query: str,
    limit: int = 50
) -> List[Movie]:
    """Search movies by title"""
    search_pattern = f"%{query}%"
    result = await session.execute(
        select(Movie)
        .where(
            Movie.is_active == True,
            or_(
                Movie.title.ilike(search_pattern),
                Movie.title_uz.ilike(search_pattern),
                Movie.title_ru.ilike(search_pattern),
                Movie.title_en.ilike(search_pattern)
            )
        )
        .order_by(Movie.views.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_movies_by_category(
    session: AsyncSession,
    category: str,
    limit: int = 50,
    offset: int = 0
) -> List[Movie]:
    """Get movies by category"""
    result = await session.execute(
        select(Movie)
        .where(Movie.is_active == True, Movie.category == category)
        .order_by(Movie.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def get_movies_by_genre(
    session: AsyncSession,
    genre_id: int,
    limit: int = 50,
    offset: int = 0
) -> List[Movie]:
    """Get movies by genre"""
    result = await session.execute(
        select(Movie)
        .join(MovieGenre)
        .where(
            Movie.is_active == True,
            MovieGenre.genre_id == genre_id
        )
        .order_by(Movie.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def get_top_movies(session: AsyncSession, limit: int = 10) -> List[Movie]:
    """Get top rated movies"""
    result = await session.execute(
        select(Movie)
        .where(Movie.is_active == True, Movie.rating_count > 0)
        .order_by(Movie.user_rating.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_popular_movies(session: AsyncSession, limit: int = 10) -> List[Movie]:
    """Get most viewed movies"""
    result = await session.execute(
        select(Movie)
        .where(Movie.is_active == True)
        .order_by(Movie.views.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_new_movies(session: AsyncSession, limit: int = 10) -> List[Movie]:
    """Get newest movies"""
    result = await session.execute(
        select(Movie)
        .where(Movie.is_active == True)
        .order_by(Movie.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_random_movie(session: AsyncSession) -> Optional[Movie]:
    """Get random movie"""
    result = await session.execute(
        select(Movie)
        .where(Movie.is_active == True)
        .order_by(func.random())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_movies_count(session: AsyncSession) -> int:
    """Get total movies count"""
    result = await session.execute(
        select(func.count(Movie.id)).where(Movie.is_active == True)
    )
    return result.scalar() or 0


# ==================== EPISODE OPERATIONS ====================

async def get_episode(session: AsyncSession, episode_id: int) -> Optional[Episode]:
    """Get episode by ID"""
    result = await session.execute(
        select(Episode).where(Episode.id == episode_id)
    )
    return result.scalar_one_or_none()


async def get_episodes_by_movie(
    session: AsyncSession,
    movie_id: int,
    season: Optional[int] = None
) -> List[Episode]:
    """Get all episodes for a movie"""
    query = select(Episode).where(Episode.movie_id == movie_id)

    if season is not None:
        query = query.where(Episode.season_number == season)

    query = query.order_by(Episode.season_number, Episode.episode_number)

    result = await session.execute(query)
    return list(result.scalars().all())


async def get_episode_by_number(
    session: AsyncSession,
    movie_id: int,
    episode_number: int,
    season_number: int = 1
) -> Optional[Episode]:
    """Get specific episode by number"""
    result = await session.execute(
        select(Episode).where(
            Episode.movie_id == movie_id,
            Episode.season_number == season_number,
            Episode.episode_number == episode_number
        )
    )
    return result.scalar_one_or_none()


async def create_episode(
    session: AsyncSession,
    movie_id: int,
    episode_number: int,
    file_id: str,
    message_id: int,
    channel_id: int,
    season_number: int = 1,
    title: Optional[str] = None,
    duration: Optional[int] = None
) -> Episode:
    """Create new episode"""
    episode = Episode(
        movie_id=movie_id,
        episode_number=episode_number,
        season_number=season_number,
        title=title,
        file_id=file_id,
        message_id=message_id,
        channel_id=channel_id,
        duration=duration
    )
    session.add(episode)

    # Update movie total_episodes
    await session.execute(
        update(Movie)
        .where(Movie.id == movie_id)
        .values(total_episodes=Movie.total_episodes + 1)
    )

    await session.commit()
    await session.refresh(episode)
    return episode


async def delete_episode(session: AsyncSession, episode_id: int) -> bool:
    """Delete episode"""
    episode = await get_episode(session, episode_id)
    if not episode:
        return False

    movie_id = episode.movie_id

    result = await session.execute(
        delete(Episode).where(Episode.id == episode_id)
    )

    # Update movie total_episodes
    await session.execute(
        update(Movie)
        .where(Movie.id == movie_id)
        .values(total_episodes=Movie.total_episodes - 1)
    )

    await session.commit()
    return result.rowcount > 0


async def get_seasons_for_movie(session: AsyncSession, movie_id: int) -> List[int]:
    """Get list of seasons for a movie"""
    result = await session.execute(
        select(Episode.season_number)
        .where(Episode.movie_id == movie_id)
        .distinct()
        .order_by(Episode.season_number)
    )
    return [row[0] for row in result.all()]


# ==================== GENRE OPERATIONS ====================

async def get_genre(session: AsyncSession, genre_id: int) -> Optional[Genre]:
    """Get genre by ID"""
    result = await session.execute(
        select(Genre).where(Genre.id == genre_id)
    )
    return result.scalar_one_or_none()


async def get_genre_by_name(session: AsyncSession, name: str) -> Optional[Genre]:
    """Get genre by name"""
    result = await session.execute(
        select(Genre).where(Genre.name == name.lower())
    )
    return result.scalar_one_or_none()


async def get_all_genres(session: AsyncSession) -> List[Genre]:
    """Get all genres"""
    result = await session.execute(select(Genre).order_by(Genre.name))
    return list(result.scalars().all())


async def create_genre(
    session: AsyncSession,
    name: str,
    name_uz: str,
    name_ru: str,
    name_en: str
) -> Genre:
    """Create new genre"""
    genre = Genre(
        name=name.lower(),
        name_uz=name_uz,
        name_ru=name_ru,
        name_en=name_en
    )
    session.add(genre)
    await session.commit()
    await session.refresh(genre)
    return genre


async def add_movie_genre(session: AsyncSession, movie_id: int, genre_id: int) -> None:
    """Add genre to movie"""
    mg = MovieGenre(movie_id=movie_id, genre_id=genre_id)
    session.add(mg)
    await session.commit()


async def get_movie_genres(session: AsyncSession, movie_id: int) -> List[Genre]:
    """Get genres for movie"""
    result = await session.execute(
        select(Genre)
        .join(MovieGenre)
        .where(MovieGenre.movie_id == movie_id)
    )
    return list(result.scalars().all())


# ==================== RATING OPERATIONS ====================

async def get_user_rating(session: AsyncSession, user_id: int, movie_id: int) -> Optional[Rating]:
    """Get user's rating for movie"""
    result = await session.execute(
        select(Rating).where(
            Rating.user_id == user_id,
            Rating.movie_id == movie_id
        )
    )
    return result.scalar_one_or_none()


async def add_rating(
    session: AsyncSession,
    user_id: int,
    movie_id: int,
    rating: int
) -> Tuple[bool, float]:
    """Add or update user rating, returns (is_new, new_average)"""
    existing = await get_user_rating(session, user_id, movie_id)

    if existing:
        existing.rating = rating
        existing.created_at = datetime.utcnow()
        is_new = False
    else:
        new_rating = Rating(user_id=user_id, movie_id=movie_id, rating=rating)
        session.add(new_rating)
        is_new = True

    await session.commit()

    # Calculate new average
    result = await session.execute(
        select(func.avg(Rating.rating), func.count(Rating.id))
        .where(Rating.movie_id == movie_id)
    )
    avg_rating, count = result.one()

    # Update movie rating
    await session.execute(
        update(Movie)
        .where(Movie.id == movie_id)
        .values(user_rating=round(avg_rating, 1), rating_count=count)
    )
    await session.commit()

    return is_new, round(avg_rating, 1)


async def get_user_ratings(session: AsyncSession, user_id: int, limit: int = 50) -> List[Tuple[Movie, int]]:
    """Get user's ratings with movies"""
    result = await session.execute(
        select(Movie, Rating.rating)
        .join(Rating, Movie.id == Rating.movie_id)
        .where(Rating.user_id == user_id)
        .order_by(Rating.created_at.desc())
        .limit(limit)
    )
    return list(result.all())


# ==================== FAVORITES OPERATIONS ====================

async def is_favorite(session: AsyncSession, user_id: int, movie_id: int) -> bool:
    """Check if movie is in user's favorites"""
    result = await session.execute(
        select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.movie_id == movie_id
        )
    )
    return result.scalar_one_or_none() is not None


async def add_favorite(session: AsyncSession, user_id: int, movie_id: int) -> bool:
    """Add movie to favorites"""
    if await is_favorite(session, user_id, movie_id):
        return False

    fav = Favorite(user_id=user_id, movie_id=movie_id)
    session.add(fav)
    await session.commit()
    return True


async def remove_favorite(session: AsyncSession, user_id: int, movie_id: int) -> bool:
    """Remove movie from favorites"""
    result = await session.execute(
        delete(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.movie_id == movie_id
        )
    )
    await session.commit()
    return result.rowcount > 0


async def get_user_favorites(session: AsyncSession, user_id: int, limit: int = 50) -> List[Movie]:
    """Get user's favorite movies"""
    result = await session.execute(
        select(Movie)
        .join(Favorite)
        .where(Favorite.user_id == user_id, Movie.is_active == True)
        .order_by(Favorite.added_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


# ==================== WATCH HISTORY OPERATIONS ====================

async def add_to_history(session: AsyncSession, user_id: int, movie_id: int) -> None:
    """Add movie to watch history"""
    history = WatchHistory(user_id=user_id, movie_id=movie_id)
    session.add(history)
    await session.commit()


async def get_user_history(session: AsyncSession, user_id: int, limit: int = 50) -> List[Movie]:
    """Get user's watch history"""
    result = await session.execute(
        select(Movie)
        .join(WatchHistory)
        .where(WatchHistory.user_id == user_id, Movie.is_active == True)
        .order_by(WatchHistory.watched_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


# ==================== CHANNEL OPERATIONS ====================

async def get_active_channels(session: AsyncSession) -> List[Channel]:
    """Get all active subscription channels"""
    result = await session.execute(
        select(Channel).where(Channel.is_active == True)
    )
    return list(result.scalars().all())


async def get_channel(session: AsyncSession, channel_id: int) -> Optional[Channel]:
    """Get channel by ID"""
    result = await session.execute(
        select(Channel).where(Channel.channel_id == channel_id)
    )
    return result.scalar_one_or_none()


async def add_channel(
    session: AsyncSession,
    channel_id: int,
    channel_username: str,
    channel_title: str
) -> Channel:
    """Add new subscription channel"""
    channel = Channel(
        channel_id=channel_id,
        channel_username=channel_username,
        channel_title=channel_title
    )
    session.add(channel)
    await session.commit()
    await session.refresh(channel)
    return channel


async def remove_channel(session: AsyncSession, channel_id: int) -> bool:
    """Remove subscription channel"""
    result = await session.execute(
        delete(Channel).where(Channel.channel_id == channel_id)
    )
    await session.commit()
    return result.rowcount > 0


async def toggle_channel(session: AsyncSession, channel_id: int) -> bool:
    """Toggle channel active status"""
    channel = await get_channel(session, channel_id)
    if channel:
        channel.is_active = not channel.is_active
        await session.commit()
        return True
    return False


# ==================== ADMIN OPERATIONS ====================

async def is_admin(session: AsyncSession, user_id: int) -> bool:
    """Check if user is admin"""
    result = await session.execute(
        select(Admin).where(Admin.user_id == user_id)
    )
    return result.scalar_one_or_none() is not None


async def is_superadmin(session: AsyncSession, user_id: int) -> bool:
    """Check if user is superadmin"""
    result = await session.execute(
        select(Admin).where(Admin.user_id == user_id, Admin.role == "superadmin")
    )
    return result.scalar_one_or_none() is not None


async def add_admin(session: AsyncSession, user_id: int, role: str = "admin") -> Admin:
    """Add new admin"""
    admin = Admin(user_id=user_id, role=role)
    session.add(admin)
    await session.commit()
    await session.refresh(admin)
    return admin


async def remove_admin(session: AsyncSession, user_id: int) -> bool:
    """Remove admin"""
    result = await session.execute(
        delete(Admin).where(Admin.user_id == user_id)
    )
    await session.commit()
    return result.rowcount > 0


async def get_all_admins(session: AsyncSession) -> List[Admin]:
    """Get all admins"""
    result = await session.execute(select(Admin))
    return list(result.scalars().all())


# ==================== TOP USERS OPERATIONS ====================

async def get_top_users_by_watches(session: AsyncSession, limit: int = 10) -> List[Tuple[User, int]]:
    """Get top users by watch count"""
    result = await session.execute(
        select(User, func.count(WatchHistory.id).label('watch_count'))
        .join(WatchHistory, User.user_id == WatchHistory.user_id)
        .group_by(User.id)
        .order_by(func.count(WatchHistory.id).desc())
        .limit(limit)
    )
    return list(result.all())


async def get_top_users_by_ratings(session: AsyncSession, limit: int = 10) -> List[Tuple[User, int]]:
    """Get top users by ratings count"""
    result = await session.execute(
        select(User, func.count(Rating.id).label('rating_count'))
        .join(Rating, User.user_id == Rating.user_id)
        .group_by(User.id)
        .order_by(func.count(Rating.id).desc())
        .limit(limit)
    )
    return list(result.all())


# ==================== STATISTICS ====================

async def get_statistics(session: AsyncSession) -> dict:
    """Get bot statistics"""
    users_count = await get_users_count(session)
    today_users = await get_today_users_count(session)
    movies_count = await get_movies_count(session)

    # Total views
    result = await session.execute(
        select(func.sum(Movie.views)).where(Movie.is_active == True)
    )
    total_views = result.scalar() or 0

    # Total ratings
    result = await session.execute(select(func.count(Rating.id)))
    total_ratings = result.scalar() or 0

    return {
        "users": users_count,
        "today_users": today_users,
        "movies": movies_count,
        "total_views": total_views,
        "total_ratings": total_ratings
    }