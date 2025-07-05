import pytest
import sys
import os
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from keyboards import (
    get_reply_menu,
    get_popular_cities_keyboard,
    cancel_city_change_keyboard,
    cities_keyboard
)


class TestKeyboards:
    """Тесты для клавиатур"""
    
    def test_get_reply_menu_subscribed(self):
        """Тест главной клавиатуры для подписанного пользователя"""
        keyboard = get_reply_menu(is_subscribed=True)
        
        assert isinstance(keyboard, ReplyKeyboardMarkup)
        assert keyboard.resize_keyboard is True
        assert keyboard.one_time_keyboard is False
        assert len(keyboard.keyboard) > 0
        
        # Проверяем наличие основных кнопок
        button_texts = [btn.text for row in keyboard.keyboard for btn in row]
        assert "поменять что-то в жизни" in button_texts
        # assert "👀Чо по погоде ?" in button_texts
        assert "чо по городу 🤌🏻" in button_texts
        assert "Популярные города" in button_texts
        assert "прогноз на 3 дня" in button_texts
        assert "🔕 Выключить автосообщения" in button_texts
    
    def test_get_reply_menu_unsubscribed(self):
        """Тест главной клавиатуры для неподписанного пользователя"""
        keyboard = get_reply_menu(is_subscribed=False)
        
        assert isinstance(keyboard, ReplyKeyboardMarkup)
        assert keyboard.resize_keyboard is True
        assert keyboard.one_time_keyboard is False
        assert len(keyboard.keyboard) > 0
        
        # Проверяем наличие кнопки подписки
        button_texts = [btn.text for row in keyboard.keyboard for btn in row]
        assert "📬 Включить автосообщения" in button_texts
    
    def test_get_popular_cities_keyboard(self):
        """Тест клавиатуры популярных городов"""
        keyboard = get_popular_cities_keyboard(page=0)
        
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) > 0
        
        # Проверяем наличие кнопки "Вперед" на первой странице
        button_texts = [btn.text for row in keyboard.inline_keyboard for btn in row]
        assert "▶️ Вперед" in button_texts
    
    def test_get_popular_cities_keyboard_last_page(self):
        """Тест клавиатуры популярных городов на последней странице"""
        keyboard = get_popular_cities_keyboard(page=10)  # Предполагаем, что это последняя страница
        
        assert isinstance(keyboard, InlineKeyboardMarkup)
        
        # Проверяем наличие кнопки "Назад" на последней странице
        button_texts = [btn.text for row in keyboard.inline_keyboard for btn in row]
        assert "◀️ Назад" in button_texts
    
    def test_cancel_city_change_keyboard(self):
        """Тест клавиатуры отмены изменения города"""
        keyboard = cancel_city_change_keyboard()
        
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 1
        
        # Проверяем наличие кнопки отмены
        button_texts = [btn.text for row in keyboard.inline_keyboard for btn in row]
        assert "❌ Отмена" in button_texts
    
    def test_cities_keyboard(self):
        """Тест клавиатуры выбора города"""
        cities = [
            {"id": "524901", "name": "Москва", "country": "Россия"},
            {"id": "536203", "name": "Санкт-Петербург", "country": "Россия"},
            {"id": "551487", "name": "Казань", "country": "Россия"}
        ]
        
        keyboard = cities_keyboard(cities=cities, page=0)
        
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) > 0
        
        # Проверяем наличие городов
        button_texts = [btn.text for row in keyboard.inline_keyboard for btn in row]
        assert "Москва, Россия" in button_texts
        assert "Санкт-Петербург, Россия" in button_texts 