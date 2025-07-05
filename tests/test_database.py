import pytest
import sys
import os
from sqlalchemy.orm import Session

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import User, db


class TestDatabase:
    """Тесты для работы с базой данных"""
    
    def test_add_user(self):
        """Тест добавления пользователя"""
        db.add_user(telegram_id=123456, username="test_user")
        
        user = db.get_user_by_id(telegram_id=123456)
        assert user is not None
        assert user.telegram_id == 123456
        assert user.username == "test_user"
    
    def test_get_user_by_id(self):
        """Тест получения пользователя по ID"""
        # Добавляем пользователя
        db.add_user(telegram_id=789012, username="another_user")
        
        # Получаем пользователя
        user = db.get_user_by_id(telegram_id=789012)
        
        assert user is not None
        assert user.telegram_id == 789012
        assert user.username == "another_user"
    
    def test_get_nonexistent_user(self):
        """Тест получения несуществующего пользователя"""
        user = db.get_user_by_id(telegram_id=999999)
        assert user is None
    
    def test_save_user_city(self):
        """Тест сохранения города пользователя"""
        # Добавляем пользователя
        db.add_user(telegram_id=111111, username="city_user")
        
        # Сохраняем город
        db.save_user_city(telegram_id=111111, username="city_user", city="Москва", city_id="524901")
        
        # Получаем город
        city_info = db.get_user_city(telegram_id=111111)
        
        assert city_info is not None
        assert city_info[0] == "Москва"
        assert city_info[1] == "524901"
    
    def test_get_user_city(self):
        """Тест получения города пользователя"""
        # Добавляем пользователя с городом
        db.add_user(telegram_id=222222, username="city_user2")
        db.save_user_city(telegram_id=222222, username="city_user2", city="Санкт-Петербург", city_id="536203")
        
        # Получаем город
        city_info = db.get_user_city(telegram_id=222222)
        
        assert city_info is not None
        assert city_info[0] == "Санкт-Петербург"
        assert city_info[1] == "536203"
    
    def test_get_nonexistent_user_city(self):
        """Тест получения города несуществующего пользователя"""
        city_info = db.get_user_city(telegram_id=888888)
        assert city_info is None
    
    def test_toggle_subscription(self):
        """Тест переключения подписки"""
        # Добавляем пользователя
        db.add_user(telegram_id=333333, username="sub_user")
        
        # Переключаем подписку
        subscription_status = db.toggle_subscription(telegram_id=333333)
        
        assert subscription_status is True
        
        # Переключаем еще раз
        subscription_status = db.toggle_subscription(telegram_id=333333)
        
        assert subscription_status is False
    
    def test_get_all_users(self):
        """Тест получения всех пользователей"""
        # Добавляем несколько пользователей
        db.add_user(telegram_id=444444, username="user1")
        db.add_user(telegram_id=555555, username="user2")
        
        users = db.get_all_users()
        
        assert len(users) >= 2
        user_ids = [user.telegram_id for user in users]
        assert 444444 in user_ids
        assert 555555 in user_ids 