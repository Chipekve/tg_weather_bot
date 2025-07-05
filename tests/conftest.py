import pytest
import asyncio
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram import Bot, Dispatcher
from aiogram.types import Message, User, Chat
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "weather_bot"))

from database import Base, User as DBUser
import weather_api


@pytest.fixture
def event_loop():
    """Создает event loop для асинхронных тестов"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def bot():
    """Создает мок бота"""
    return AsyncMock(spec=Bot)


@pytest.fixture
def dispatcher():
    """Создает диспетчер для тестов"""
    return Dispatcher()


@pytest.fixture
def mock_message():
    """Создает мок сообщения"""
    message = AsyncMock(spec=Message)
    message.from_user = AsyncMock(spec=User)
    message.from_user.id = 123456
    message.from_user.first_name = "Test"
    message.from_user.username = "test_user"
    message.chat = AsyncMock(spec=Chat)
    message.chat.id = 123456
    message.text = "test"
    return message


@pytest.fixture
def test_db():
    """Создает тестовую базу данных в памяти"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def mock_weather_api():
    """Создает мок API погоды"""
    with patch('weather_api.fetch_weather') as mock_fetch:
        mock_fetch.return_value = {
            "current": {
                "temp_c": 20,
                "condition": {"text": "Солнечно"},
                "humidity": 60,
                "wind_kph": 5
            }
        }
        yield mock_fetch 