"""
Localization - Multi-language support
Languages: uz (O'zbek), ru (Русский), en (English)
"""

TEXTS = {
    # ==================== COMMON ====================
    "welcome": {
        "uz": "👋 Assalomu alaykum, {name}!\n\n🎬 Kino botga xush kelibsiz!\n\nKino kodini yuboring va kinoni oling.",
        "ru": "👋 Привет, {name}!\n\n🎬 Добро пожаловать в кино бот!\n\nОтправьте код фильма, чтобы получить его.",
        "en": "👋 Hello, {name}!\n\n🎬 Welcome to Movie Bot!\n\nSend movie code to get it."
    },
    
    "choose_language": {
        "uz": "🌐 Tilni tanlang:",
        "ru": "🌐 Выберите язык:",
        "en": "🌐 Choose language:"
    },
    
    "language_changed": {
        "uz": "✅ Til o'zgartirildi: O'zbekcha",
        "ru": "✅ Язык изменен: Русский",
        "en": "✅ Language changed: English"
    },
    
    "help": {
        "uz": """📚 <b>Yordam</b>

🔢 <b>Kino kodi</b> - Kino kodini yuboring
🔍 <b>/search</b> - Kino qidirish
🏆 <b>/top</b> - Top 10 kinolar
🆕 <b>/new</b> - Yangi kinolar
🔥 <b>/popular</b> - Mashxur kinolar
🎲 <b>/random</b> - Tasodifiy kino
🎭 <b>/genres</b> - Janrlar
❤️ <b>/favorites</b> - Sevimlilar
🌐 <b>/language</b> - Til o'zgartirish

📽 Inline qidiruv: @{bot_username} kino nomi""",
        
        "ru": """📚 <b>Помощь</b>

🔢 <b>Код фильма</b> - Отправьте код фильма
🔍 <b>/search</b> - Поиск фильма
🏆 <b>/top</b> - Топ 10 фильмов
🆕 <b>/new</b> - Новые фильмы
🔥 <b>/popular</b> - Популярные фильмы
🎲 <b>/random</b> - Случайный фильм
🎭 <b>/genres</b> - Жанры
❤️ <b>/favorites</b> - Избранное
🌐 <b>/language</b> - Сменить язык

📽 Поиск inline: @{bot_username} название""",
        
        "en": """📚 <b>Help</b>

🔢 <b>Movie code</b> - Send movie code
🔍 <b>/search</b> - Search movie
🏆 <b>/top</b> - Top 10 movies
🆕 <b>/new</b> - New movies
🔥 <b>/popular</b> - Popular movies
🎲 <b>/random</b> - Random movie
🎭 <b>/genres</b> - Genres
❤️ <b>/favorites</b> - Favorites
🌐 <b>/language</b> - Change language

📽 Inline search: @{bot_username} movie name"""
    },
    
    # ==================== SUBSCRIPTION ====================
    "subscribe_required": {
        "uz": "⚠️ Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:",
        "ru": "⚠️ Чтобы использовать бота, подпишитесь на каналы:",
        "en": "⚠️ Subscribe to channels to use the bot:"
    },
    
    "check_subscription": {
        "uz": "✅ Obunani tekshirish",
        "ru": "✅ Проверить подписку",
        "en": "✅ Check subscription"
    },
    
    "not_subscribed": {
        "uz": "❌ Siz hali barcha kanallarga obuna bo'lmadingiz!",
        "ru": "❌ Вы не подписаны на все каналы!",
        "en": "❌ You are not subscribed to all channels!"
    },
    
    "subscribed_success": {
        "uz": "✅ Rahmat! Endi botdan foydalanishingiz mumkin.",
        "ru": "✅ Спасибо! Теперь вы можете использовать бота.",
        "en": "✅ Thanks! Now you can use the bot."
    },
    
    # ==================== MOVIES ====================
    "movie_not_found": {
        "uz": "❌ Kino topilmadi. Kodni tekshiring.",
        "ru": "❌ Фильм не найден. Проверьте код.",
        "en": "❌ Movie not found. Check the code."
    },
    
    "movie_info": {
        "uz": """🎬 <b>{title}</b>
➖➖➖➖➖➖➖
📅 <b>Yil:</b> {year}
🌐 <b>Til:</b> {language}
📺 <b>Sifat:</b> {quality}
🎭 <b>Janr:</b> {genres}
📁 <b>Kategoriya:</b> {category}

⭐ <b>Reyting:</b> {rating} ({count} ta baho)
👁 <b>Ko'rishlar:</b> {views}

🆔 <b>Kod:</b> <code>{id}</code>""",
        
        "ru": """🎬 <b>{title}</b>

📅 <b>Год:</b> {year}
🌐 <b>Язык:</b> {language}
📺 <b>Качество:</b> {quality}
🎭 <b>Жанр:</b> {genres}
📁 <b>Категория:</b> {category}

⭐ <b>Рейтинг:</b> {rating} ({count} оценок)
👁 <b>Просмотры:</b> {views}

🆔 Код: <code>{id}</code>""",
        
        "en": """🎬 <b>{title}</b>

📅 <b>Year:</b> {year}
🌐 <b>Language:</b> {language}
📺 <b>Quality:</b> {quality}
🎭 <b>Genre:</b> {genres}
📁 <b>Category:</b> {category}

⭐ <b>Rating:</b> {rating} ({count} votes)
👁 <b>Views:</b> {views}

🆔 Code: <code>{id}</code>"""
    },
    
    # ==================== SEARCH ====================
    "search_prompt": {
        "uz": "🔍 Kino nomini kiriting:",
        "ru": "🔍 Введите название фильма:",
        "en": "🔍 Enter movie name:"
    },
    
    "search_results": {
        "uz": "🔍 Qidiruv natijalari: \"{query}\"\n\n{count} ta kino topildi:",
        "ru": "🔍 Результаты поиска: \"{query}\"\n\n{count} фильмов найдено:",
        "en": "🔍 Search results: \"{query}\"\n\n{count} movies found:"
    },
    
    "search_no_results": {
        "uz": "😔 \"{query}\" bo'yicha hech narsa topilmadi.",
        "ru": "😔 По запросу \"{query}\" ничего не найдено.",
        "en": "😔 Nothing found for \"{query}\"."
    },
    
    "search_cancelled": {
        "uz": "❌ Qidiruv bekor qilindi.",
        "ru": "❌ Поиск отменен.",
        "en": "❌ Search cancelled."
    },
    
    # ==================== LISTS ====================
    "top_movies": {
        "uz": "🏆 <b>Top 10 kinolar</b>\n\n",
        "ru": "🏆 <b>Топ 10 фильмов</b>\n\n",
        "en": "🏆 <b>Top 10 movies</b>\n\n"
    },
    
    "new_movies": {
        "uz": "🆕 <b>Yangi kinolar</b>\n\n",
        "ru": "🆕 <b>Новые фильмы</b>\n\n",
        "en": "🆕 <b>New movies</b>\n\n"
    },
    
    "popular_movies": {
        "uz": "🔥 <b>Mashxur kinolar</b>\n\n",
        "ru": "🔥 <b>Популярные фильмы</b>\n\n",
        "en": "🔥 <b>Popular movies</b>\n\n"
    },
    
    "random_movie": {
        "uz": "🎲 Tasodifiy kino:",
        "ru": "🎲 Случайный фильм:",
        "en": "🎲 Random movie:"
    },
    
    "no_movies": {
        "uz": "😔 Kinolar topilmadi.",
        "ru": "😔 Фильмы не найдены.",
        "en": "😔 No movies found."
    },
    
    # ==================== GENRES ====================
    "genres_list": {
        "uz": "🎭 <b>Janrlar</b>\n\nJanrni tanlang:",
        "ru": "🎭 <b>Жанры</b>\n\nВыберите жанр:",
        "en": "🎭 <b>Genres</b>\n\nSelect genre:"
    },
    
    "genre_movies": {
        "uz": "🎭 <b>{genre}</b> janridagi kinolar:\n\n",
        "ru": "🎭 Фильмы жанра <b>{genre}</b>:\n\n",
        "en": "🎭 <b>{genre}</b> movies:\n\n"
    },
    
    # ==================== FAVORITES ====================
    "favorites_list": {
        "uz": "❤️ <b>Sevimli kinolar</b>\n\n",
        "ru": "❤️ <b>Избранные фильмы</b>\n\n",
        "en": "❤️ <b>Favorite movies</b>\n\n"
    },
    
    "favorites_empty": {
        "uz": "😔 Sevimlilar ro'yxati bo'sh.",
        "ru": "😔 Список избранного пуст.",
        "en": "😔 Favorites list is empty."
    },
    
    "added_to_favorites": {
        "uz": "❤️ Sevimlilarga qo'shildi!",
        "ru": "❤️ Добавлено в избранное!",
        "en": "❤️ Added to favorites!"
    },
    
    "removed_from_favorites": {
        "uz": "💔 Sevimlilardan olib tashlandi.",
        "ru": "💔 Удалено из избранного.",
        "en": "💔 Removed from favorites."
    },
    
    "already_in_favorites": {
        "uz": "⚠️ Bu kino allaqachon sevimlilarda.",
        "ru": "⚠️ Этот фильм уже в избранном.",
        "en": "⚠️ This movie is already in favorites."
    },
    
    # ==================== HISTORY ====================
    "history_list": {
        "uz": "📜 <b>Ko'rish tarixi</b>\n\n",
        "ru": "📜 <b>История просмотров</b>\n\n",
        "en": "📜 <b>Watch history</b>\n\n"
    },
    
    "history_empty": {
        "uz": "😔 Tarix bo'sh.",
        "ru": "😔 История пуста.",
        "en": "😔 History is empty."
    },
    
    # ==================== RATING ====================
    "rate_movie": {
        "uz": "⭐ Kinoni baholang:",
        "ru": "⭐ Оцените фильм:",
        "en": "⭐ Rate the movie:"
    },
    
    "rating_saved": {
        "uz": "✅ Bahoyingiz saqlandi! Yangi reyting: ⭐ {rating}",
        "ru": "✅ Ваша оценка сохранена! Новый рейтинг: ⭐ {rating}",
        "en": "✅ Your rating is saved! New rating: ⭐ {rating}"
    },
    
    "my_ratings": {
        "uz": "⭐ <b>Mening baholarim</b>\n\n",
        "ru": "⭐ <b>Мои оценки</b>\n\n",
        "en": "⭐ <b>My ratings</b>\n\n"
    },
    
    "ratings_empty": {
        "uz": "😔 Siz hali hech qanday kinoni baholamadingiz.",
        "ru": "😔 Вы еще не оценили ни одного фильма.",
        "en": "😔 You haven't rated any movies yet."
    },
    
    # ==================== BUTTONS ====================
    "btn_rate": {
        "uz": "⭐ Baholash",
        "ru": "⭐ Оценить",
        "en": "⭐ Rate"
    },
    
    "btn_favorite": {
        "uz": "❤️ Sevimlilarga",
        "ru": "❤️ В избранное",
        "en": "❤️ Add to favorites"
    },
    
    "btn_unfavorite": {
        "uz": "💔 Sevimlilardan",
        "ru": "💔 Из избранного",
        "en": "💔 Remove from favorites"
    },
    
    "btn_back": {
        "uz": "🔙 Orqaga",
        "ru": "🔙 Назад",
        "en": "🔙 Back"
    },
    
    "btn_cancel": {
        "uz": "❌ Bekor qilish",
        "ru": "❌ Отмена",
        "en": "❌ Cancel"
    },
    
    "btn_skip": {
        "uz": "⏭ O'tkazib yuborish",
        "ru": "⏭ Пропустить",
        "en": "⏭ Skip"
    },
    
    "btn_save": {
        "uz": "✅ Saqlash",
        "ru": "✅ Сохранить",
        "en": "✅ Save"
    },
    
    # ==================== ADMIN ====================
    "admin_panel": {
        "uz": """👨‍💼 <b>Admin panel</b>

📊 Statistika:
👥 Jami foydalanuvchilar: {users}
👤 Bugun qo'shilgan: {today_users}
🎬 Jami kinolar: {movies}
👁 Jami ko'rishlar: {views}
⭐ Jami baholar: {ratings}""",
        
        "ru": """👨‍💼 <b>Админ панель</b>

📊 Статистика:
👥 Всего пользователей: {users}
👤 Новых сегодня: {today_users}
🎬 Всего фильмов: {movies}
👁 Всего просмотров: {views}
⭐ Всего оценок: {ratings}""",
        
        "en": """👨‍💼 <b>Admin panel</b>

📊 Statistics:
👥 Total users: {users}
👤 New today: {today_users}
🎬 Total movies: {movies}
👁 Total views: {views}
⭐ Total ratings: {ratings}"""
    },
    
    "not_admin": {
        "uz": "⛔ Sizda admin huquqi yo'q!",
        "ru": "⛔ У вас нет прав администратора!",
        "en": "⛔ You don't have admin rights!"
    },
    
    # ==================== MOVIE ADD ====================
    "new_video_detected": {
        "uz": "📽 Yangi video aniqlandi!\n\nKino nomini kiriting:",
        "ru": "📽 Обнаружено новое видео!\n\nВведите название фильма:",
        "en": "📽 New video detected!\n\nEnter movie title:"
    },
    
    "enter_year": {
        "uz": "📅 Yilni tanlang yoki kiriting:",
        "ru": "📅 Выберите или введите год:",
        "en": "📅 Select or enter year:"
    },
    
    "select_language": {
        "uz": "🌐 Kino tilini tanlang:",
        "ru": "🌐 Выберите язык фильма:",
        "en": "🌐 Select movie language:"
    },
    
    "select_quality": {
        "uz": "📺 Sifatni tanlang:",
        "ru": "📺 Выберите качество:",
        "en": "📺 Select quality:"
    },
    
    "select_category": {
        "uz": "📁 Kategoriyani tanlang:",
        "ru": "📁 Выберите категорию:",
        "en": "📁 Select category:"
    },
    
    "select_genres": {
        "uz": "🎭 Janrlarni tanlang (bir nechta bo'lishi mumkin):",
        "ru": "🎭 Выберите жанры (можно несколько):",
        "en": "🎭 Select genres (multiple allowed):"
    },
    
    "enter_duration": {
        "uz": "⏱ Davomiyligini kiriting (minutlarda) yoki o'tkazib yuboring:",
        "ru": "⏱ Введите длительность (в минутах) или пропустите:",
        "en": "⏱ Enter duration (in minutes) or skip:"
    },
    
    "movie_added": {
        "uz": "✅ Kino muvaffaqiyatli qo'shildi!\n\n🆔 Kino kodi: <code>{id}</code>",
        "ru": "✅ Фильм успешно добавлен!\n\n🆔 Код фильма: <code>{id}</code>",
        "en": "✅ Movie added successfully!\n\n🆔 Movie code: <code>{id}</code>"
    },
    
    "movie_add_cancelled": {
        "uz": "❌ Kino qo'shish bekor qilindi.",
        "ru": "❌ Добавление фильма отменено.",
        "en": "❌ Movie adding cancelled."
    },
    
    "movie_deleted": {
        "uz": "✅ Kino o'chirildi.",
        "ru": "✅ Фильм удален.",
        "en": "✅ Movie deleted."
    },
    
    # ==================== CHANNELS ====================
    "channels_list": {
        "uz": "📢 <b>Majburiy obuna kanallari:</b>\n\n",
        "ru": "📢 <b>Каналы обязательной подписки:</b>\n\n",
        "en": "📢 <b>Required subscription channels:</b>\n\n"
    },
    
    "no_channels": {
        "uz": "📢 Kanallar yo'q.",
        "ru": "📢 Каналов нет.",
        "en": "📢 No channels."
    },
    
    "channel_added": {
        "uz": "✅ Kanal qo'shildi: {title}",
        "ru": "✅ Канал добавлен: {title}",
        "en": "✅ Channel added: {title}"
    },
    
    "channel_removed": {
        "uz": "✅ Kanal olib tashlandi.",
        "ru": "✅ Канал удален.",
        "en": "✅ Channel removed."
    },
    
    "forward_channel_msg": {
        "uz": "📢 Kanaldan biror xabarni forward qiling:",
        "ru": "📢 Перешлите сообщение из канала:",
        "en": "📢 Forward a message from the channel:"
    },
    
    # ==================== BROADCAST ====================
    "broadcast_prompt": {
        "uz": "📨 Yubormoqchi bo'lgan xabaringizni yuboring:",
        "ru": "📨 Отправьте сообщение для рассылки:",
        "en": "📨 Send the message to broadcast:"
    },
    
    "broadcast_confirm": {
        "uz": "📨 {count} ta foydalanuvchiga yuborilsinmi?",
        "ru": "📨 Отправить {count} пользователям?",
        "en": "📨 Send to {count} users?"
    },
    
    "broadcast_started": {
        "uz": "📨 Xabar yuborish boshlandi...",
        "ru": "📨 Рассылка началась...",
        "en": "📨 Broadcast started..."
    },
    
    "broadcast_done": {
        "uz": "✅ Xabar yuborildi!\n\n✅ Muvaffaqiyatli: {success}\n❌ Xato: {failed}",
        "ru": "✅ Рассылка завершена!\n\n✅ Успешно: {success}\n❌ Ошибок: {failed}",
        "en": "✅ Broadcast done!\n\n✅ Success: {success}\n❌ Failed: {failed}"
    },
    
    # ==================== TOP USERS ====================
    "top_users": {
        "uz": "🏆 <b>Top foydalanuvchilar</b>\n\n",
        "ru": "🏆 <b>Топ пользователи</b>\n\n",
        "en": "🏆 <b>Top users</b>\n\n"
    },
    
    # ==================== ERRORS ====================
    "error_occurred": {
        "uz": "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.",
        "ru": "❌ Произошла ошибка. Попробуйте снова.",
        "en": "❌ An error occurred. Please try again."
    },
    
    "invalid_input": {
        "uz": "⚠️ Noto'g'ri ma'lumot kiritildi.",
        "ru": "⚠️ Неверный ввод данных.",
        "en": "⚠️ Invalid input."
    },
    
    "user_banned": {
        "uz": "⛔ Siz bloklangansiz.",
        "ru": "⛔ Вы заблокированы.",
        "en": "⛔ You are banned."
    },
}


def get_text(key: str, lang: str = "uz", **kwargs) -> str:
    """Get localized text"""
    text_dict = TEXTS.get(key, {})
    text = text_dict.get(lang, text_dict.get("uz", key))
    
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    
    return text


def t(key: str, lang: str = "uz", **kwargs) -> str:
    """Shortcut for get_text"""
    return get_text(key, lang, **kwargs)
