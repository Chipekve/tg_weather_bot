# 🌤 Weather Bot

Telegram-бот для получения прогноза погоды с функциями выбора города, подписки на рассылку и защитой от спама.



## Возможности

- **Прогноз погоды** - получение текущей погоды для любого города
- **Выбор города** - удобный интерфейс для выбора города
- **Популярные города** - быстрый доступ к популярным городам
- **Подписка на рассылку** - автоматическая рассылка прогноза погоды
- **Защита от спама** - middleware для ограничения частоты запросов
- **Docker поддержка** - готовые контейнеры для развертывания

## Технологии

- **Python 3.9+** - основной язык
- **aiogram 3.x** - Telegram Bot API
- **SQLAlchemy** - ORM для работы с базой данных
- **PostgreSQL** - основная база данных
- **Docker & Docker Compose** - контейнеризация
- **OpenWeatherMap API** - данные о погоде

## 📁 Структура проекта

```
weather_bot/
├── bot.py                 # Основной файл бота
├── database.py            # Модели и функции БД
├── weather_api.py         # API для получения погоды
├── keyboards.py           # Клавиатуры бота
├── middlewares.py         # Middleware для антиспама
├── popular_cities.py      # Список популярных городов
├── handlers/              # Обработчики команд
│   ├── start.py          # Обработчик /start
│   ├── weather.py        # Обработчик погоды
│   ├── city_selection.py # Выбор города
│   ├── popular.py        # Популярные города
│   └── weather_sender.py # Рассылка погоды
├── tests/                 # Тесты
│   ├── conftest.py       # Фикстуры pytest
│   ├── test_database.py  # Тесты БД
│   ├── test_weather_api.py # Тесты API погоды
│   ├── test_keyboards.py # Тесты клавиатур
│   └── test_middlewares.py # Тесты middleware
├── docker-compose.yml     # Docker Compose конфигурация
├── Dockerfile            # Docker образ
├── requirements.txt      # Зависимости Python
├── requirements-test.txt # Зависимости для тестов
├── env.example          # Пример .env файла
├── deploy.sh            # Скрипт деплоя
└── README.md            # Документация
```

## Быстрый старт

### Локальная разработка

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/Chipekve/tg_weather_bot.git
cd weather_bot
```

2. **Создайте виртуальное окружение:**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate     # Windows
```

3. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

4. **Настройте переменные окружения:**
```bash
cp env.example .env
# Отредактируйте .env файл, добавив свои токены
```

5. **Запустите бота:**
```bash
python bot.py
```

### Docker

1. **Клонируйте и настройте:**
```bash
git clone https://github.com/Chipekve/tg_weather_bot.git
cd weather_bot
cp env.example .env
# Отредактируйте .env файл
```

2. **Запустите с Docker Compose:**
```bash
docker-compose up -d
```

## Тестирование

### Установка зависимостей для тестов
```bash
pip install -r requirements-test.txt
```

### Запуск тестов
```bash
# Все тесты
pytest

# С подробным выводом
pytest -v

# Конкретный тест
pytest tests/test_database.py::TestDatabase::test_create_user

# Асинхронные тесты
pytest -m asyncio
```

### Структура тестов
- **test_database.py** - тесты работы с базой данных
- **test_weather_api.py** - тесты API погоды
- **test_keyboards.py** - тесты клавиатур
- **test_middlewares.py** - тесты middleware

## 🐳 Docker

### Сборка образа
```bash
docker build -t weather-bot .
```

### Запуск контейнера
```bash
docker run -d --name weather-bot --env-file .env weather-bot
```

### Docker Compose
```bash
# Запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

## Деплой на VPS

### Подготовка сервера
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Деплой бота
```bash
# Клонирование репозитория
git clone https://github.com/Chipekve/tg_weather_bot.git
cd weather_bot

# Настройка переменных окружения
cp env.example .env
nano .env  # Отредактируйте файл

# Запуск
docker-compose up -d
```

## Конфигурация

### Переменные окружения (.env)

```env
# Telegram Bot
BOT_TOKEN=your_bot_token_here

# Weather API
WEATHER_API_KEY=your_openweathermap_api_key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/weather_bot

# Redis (опционально)
REDIS_URL=redis://localhost:6379/0
```

### Получение токенов

1. **Telegram Bot Token:**
   - Напишите @BotFather в Telegram
   - Создайте нового бота командой `/newbot`
   - Получите токен

2. **OpenWeatherMap API Key:**
   - Зарегистрируйтесь на [OpenWeatherMap](https://openweathermap.org/)
   - Получите бесплатный API ключ

## Мониторинг

### Логи
```bash
# Просмотр логов бота
docker-compose logs -f bot

# Просмотр логов базы данных
docker-compose logs -f db
```

### Статистика
- Логи сохраняются в папку `logs/`
- База данных PostgreSQL
- Автоматическое резервное копирование

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

---
