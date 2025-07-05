import pytest
import sys
import os
from unittest.mock import AsyncMock, MagicMock
from aiogram.types import Message, User, Chat

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from middlewares import ThrottlingMiddleware


class TestThrottlingMiddleware:
    """Тесты для middleware антиспама"""
    
    @pytest.fixture
    def middleware(self):
        """Создает экземпляр middleware"""
        return ThrottlingMiddleware(rate_limit=1.0)
    
    @pytest.fixture
    def mock_message(self):
        """Создает мок сообщения"""
        message = AsyncMock(spec=Message)
        message.from_user = AsyncMock(spec=User)
        message.from_user.id = 123456
        message.chat = AsyncMock(spec=Chat)
        message.chat.id = 123456
        return message
    
    @pytest.mark.asyncio
    async def test_throttling_first_message(self, middleware, mock_message):
        """Тест первого сообщения (должно пройти)"""
        handler = AsyncMock()
        data = {"message": mock_message}
        
        await middleware(handler, mock_message, data)
        
        handler.assert_called_once_with(mock_message, data)
    
    @pytest.mark.asyncio
    async def test_throttling_rapid_messages(self, middleware, mock_message):
        """Тест быстрых сообщений (второе должно быть заблокировано)"""
        handler = AsyncMock()
        data = {"message": mock_message}
        
        # Первое сообщение
        await middleware(handler, mock_message, data)
        handler.assert_called_once()
        
        # Сбрасываем счетчик вызовов
        handler.reset_mock()
        
        # Второе сообщение сразу (должно быть заблокировано)
        await middleware(handler, mock_message, data)
        handler.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_throttling_different_users(self, middleware):
        """Тест разных пользователей (не должны блокировать друг друга)"""
        handler = AsyncMock()
        
        # Сообщение от первого пользователя
        message1 = AsyncMock(spec=Message)
        message1.from_user = AsyncMock(spec=User)
        message1.from_user.id = 123456
        message1.chat = AsyncMock(spec=Chat)
        message1.chat.id = 123456
        
        data1 = {"message": message1}
        await middleware(handler, message1, data1)
        
        # Сбрасываем счетчик
        handler.reset_mock()
        
        # Сообщение от второго пользователя (должно пройти)
        message2 = AsyncMock(spec=Message)
        message2.from_user = AsyncMock(spec=User)
        message2.from_user.id = 789012
        message2.chat = AsyncMock(spec=Chat)
        message2.chat.id = 789012
        
        data2 = {"message": message2}
        await middleware(handler, message2, data2)
        
        handler.assert_called_once_with(message2, data2) 