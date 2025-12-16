# 🎬 Kino Bot

Telegram bot for movie sharing with subscription checking, ratings, and multi-language support.

## ✨ Features

- **Movie Management**
  - Add movies via caption parsing (auto-detect)
  - Add movies via inline buttons
  - Add movies via minimal mode
  - Edit and delete movies

- **User Features**
  - Search movies by name
  - Inline search (`@bot movie_name`)
  - Rate movies (1-5 stars)
  - Add to favorites
  - Watch history
  - Multi-language (uz/ru/en)

- **Admin Features**
  - Statistics dashboard
  - Channel management
  - Broadcast messages
  - Top users view
  - Admin management

- **Security**
  - Forced subscription check
  - User ban system
  - Rate limiting

## 📋 Requirements

- Python 3.10+
- PostgreSQL or MySQL
- Telegram Bot Token

## 🚀 Installation

### 1. Clone and setup

```bash
cd kino_bot
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 2. Configure

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:

```env
BOT_TOKEN=your_bot_token_here
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/kino_bot
MOVIE_CHANNEL_ID=-1001234567890
SUPER_ADMIN_IDS=123456789
```

### 3. Setup Database

**PostgreSQL:**
```sql
CREATE DATABASE kino_bot;
```

**MySQL:**
```sql
CREATE DATABASE kino_bot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. Run

```bash
python bot.py
```

## 📁 Project Structure

```
kino_bot/
├── bot.py                    # Main entry point
├── config.py                 # Configuration
├── database/
│   ├── __init__.py          # DB engine
│   ├── models.py            # SQLAlchemy models
│   └── crud.py              # Database operations
├── handlers/
│   ├── user/                # User handlers
│   │   ├── start.py
│   │   ├── movie.py
│   │   ├── search.py
│   │   └── lists.py
│   ├── admin/               # Admin handlers
│   │   ├── panel.py
│   │   ├── movie.py
│   │   ├── channel.py
│   │   └── broadcast.py
│   └── inline.py            # Inline search
├── keyboards/               # Keyboards
├── middlewares/             # Middlewares
├── locales/                 # Translations
├── states/                  # FSM states
└── utils/                   # Utilities
```

## 🎬 Adding Movies

### Method 1: Caption Parsing (Recommended)

Post video to movie channel with caption:

```
Movie Name | 2024 | Action, Drama | O'zbek | 1080p | 120 min

Description here...
```

Bot will automatically parse and add the movie.

### Method 2: Inline Buttons

1. Post video to channel (without caption)
2. Use `/add_movie` command
3. Follow the inline button prompts

### Method 3: Minimal Mode

1. Post video to channel
2. Bot asks only for movie name
3. Other fields use defaults

## 📝 Commands

### User Commands

| Command | Description |
|---------|-------------|
| /start | Start bot |
| /search | Search movies |
| /top | Top 10 rated |
| /new | New movies |
| /popular | Popular movies |
| /random | Random movie |
| /genres | Browse by genre |
| /favorites | My favorites |
| /history | Watch history |
| /my_ratings | My ratings |
| /language | Change language |
| /help | Help |

### Admin Commands

| Command | Description |
|---------|-------------|
| /admin | Admin panel |
| /add_movie | Add movie |
| /delete_movie [id] | Delete movie |
| /edit_[id] | Edit movie |
| /stats | Statistics |
| /add_channel | Add channel |
| /channels | List channels |
| /broadcast | Send broadcast |

## 🔧 Configuration

### Database

**Local (PostgreSQL):**
```env
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/kino_bot
```

**Server (MySQL):**
```env
DATABASE_TYPE=mysql
DATABASE_URL=mysql+aiomysql://root:root@localhost:3306/kino_bot
```

### Movie Channel

1. Create a private channel for storing movies
2. Add bot as admin with post permissions
3. Get channel ID (forward message to @userinfobot)
4. Set `MOVIE_CHANNEL_ID` in `.env`

### Subscription Channels

Add channels via admin panel or `/add_channel` command.

## 🌐 Localization

Supported languages:
- 🇺🇿 O'zbek (uz)
- 🇷🇺 Русский (ru)
- 🇬🇧 English (en)

Add translations in `locales/__init__.py`

## 📊 Database Schema

- **users** - User accounts
- **movies** - Movie catalog
- **genres** - Genre list
- **movie_genres** - Movie-genre relations
- **ratings** - User ratings
- **favorites** - User favorites
- **watch_history** - Watch history
- **channels** - Subscription channels
- **admins** - Bot admins

## 🔒 Security

- Admin commands require admin role
- Subscription middleware checks all messages
- Banned users cannot use bot
- Rate limiting prevents spam

## 📈 Statistics

Admin panel shows:
- Total users
- Today's new users
- Total movies
- Total views
- Total ratings

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

MIT License

## 👤 Author

Created with ❤️
