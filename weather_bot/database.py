import os
import logging

from typing import Optional, Tuple
from sqlalchemy import create_engine, select
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import BigInteger, String, Column, Boolean, Integer

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///users.db")  # fallback на SQLite

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String)
    city = Column(String)
    city_id = Column(String)
    is_subscribed = Column(Boolean, default=False)


class Database:
    """Класс для работы с базой данных пользователей."""
    
    def __init__(self):
        Base.metadata.create_all(bind=engine)

    def save_user_city(
        self, telegram_id: int, username: str, city: str, city_id: Optional[str] = None
    ):
        """
        Сохраняет или обновляет город пользователя.
        
        Args:
            telegram_id: Telegram ID пользователя
            username: Имя пользователя
            city: Название города
            city_id: ID города в WeatherAPI
        """
        session: Session = SessionLocal()
        try:
            user = session.execute(
                select(User).where(User.telegram_id == telegram_id)
            ).scalar_one_or_none()
            if user:
                user.username = username or "anonymous"
                user.city = city
                user.city_id = city_id
            else:
                user = User(
                    telegram_id=telegram_id,
                    username=username or "anonymous",
                    city=city,
                    city_id=city_id,
                )
                session.add(user)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Ошибка при сохранении пользователя: {e}", exc_info=True)
        finally:
            session.close()

    def close(self):
        """Закрывает соединение с базой данных."""
        engine.dispose()

    def get_user_city(
        self, telegram_id: int
    ) -> Optional[Tuple[Optional[str], Optional[str]]]:
        """
        Получает город пользователя.
        
        Args:
            telegram_id: Telegram ID пользователя
            
        Returns:
            Кортеж (название города, ID города) или None
        """
        session: Session = SessionLocal()
        try:
            user = session.execute(
                select(User).where(User.telegram_id == telegram_id)
            ).scalar_one_or_none()
            if user:
                return user.city, user.city_id
            return None
        except SQLAlchemyError as e:
            logging.error(f"Ошибка при получении города: {e}", exc_info=True)
            return None
        finally:
            session.close()

    def get_user_by_id(self, telegram_id: int) -> Optional[User]:
        """
        Получает пользователя по Telegram ID.
        
        Args:
            telegram_id: Telegram ID пользователя
            
        Returns:
            Объект User или None
        """
        session: Session = SessionLocal()
        try:
            user = session.execute(
                select(User).where(User.telegram_id == telegram_id)
            ).scalar_one_or_none()
            return user
        except SQLAlchemyError as e:
            logging.error(f"Ошибка при получении пользователя: {e}", exc_info=True)
            return None
        finally:
            session.close()

    def add_user(self, telegram_id: int, username: Optional[str] = None) -> None:
        """
        Добавляет нового пользователя.
        
        Args:
            telegram_id: Telegram ID пользователя
            username: Имя пользователя (опционально)
        """
        session: Session = SessionLocal()
        try:
            new_user = User(telegram_id=telegram_id, username=username)
            session.add(new_user)
            session.commit()
        except SQLAlchemyError as e:
            logging.error(f"Ошибка при добавлении пользователя: {e}", exc_info=True)
            session.rollback()
        finally:
            session.close()

    def get_all_users(self) -> list[User]:
        """
        Получает всех пользователей.
        
        Returns:
            Список всех пользователей
        """
        session: Session = SessionLocal()
        try:
            users = session.execute(select(User)).scalars().all()
            return users
        except SQLAlchemyError as e:
            logging.error(f"Ошибка при получении всех пользователей: {e}", exc_info=True)
            return []
        finally:
            session.close()

    def toggle_subscription(self, telegram_id: int) -> Optional[bool]:
        """
        Переключает статус подписки пользователя.
        
        Args:
            telegram_id: Telegram ID пользователя
            
        Returns:
            Новый статус подписки или None при ошибке
        """
        session: Session = SessionLocal()
        try:
            user = session.execute(
                select(User).where(User.telegram_id == telegram_id)
            ).scalar_one_or_none()
            if user:
                user.is_subscribed = not user.is_subscribed
                session.commit()
                return user.is_subscribed
            return None
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Ошибка при переключении подписки: {e}", exc_info=True)
            return None
        finally:
            session.close()


db = Database()