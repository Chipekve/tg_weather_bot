# Weather Bot

Telegram-бот для получения прогноза погоды с использованием WeatherAPI.

## Возможности

- 🌤 Получение текущей погоды
- 📅 Прогноз на 3 дня
- 🏙️ Поиск и выбор городов
- 📍 Популярные города
- 📬 Автоматическая рассылка прогноза
- 🛡️ Защита от спама
- 💾 Сохранение настроек пользователей

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd weather_bot
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` с переменными окружения:
```env
BOT_TOKEN=your_telegram_bot_token
WEATHER_API_KEY=your_weather_api_key
DATABASE_URL=postgresql://user:password@localhost/dbname
```

4. Запустите бота:
```bash
python bot.py
```

## Структура проекта

```
weather_bot/
├── bot.py                 # Основной файл бота
├── database.py            # Работа с базой данных
├── weather_api.py         # API для погоды
├── keyboards.py           # Клавиатуры и константы
├── middlewares.py         # Middleware для защиты от спама
├── popular_cities.py      # Список популярных городов
├── handlers/              # Обработчики команд
│   ├── start.py          # Команда /start
│   ├── weather.py        # Погода и прогноз
│   ├── city_selection.py # Выбор города
│   ├── popular.py        # Популярные города
│   └── weather_sender.py # Авторассылка
└── requirements.txt       # Зависимости
```

## Технологии

- **aiogram 3.x** - Telegram Bot API
- **SQLAlchemy** - ORM для работы с БД
- **aiohttp** - Асинхронные HTTP запросы
- **WeatherAPI** - API погоды
- **PostgreSQL/SQLite** - База данных

## Команды бота

- `/start` - Начало работы с ботом
- Кнопки для навигации по функциям

## Лицензия

MIT 