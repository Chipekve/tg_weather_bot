import os
from typing import Optional, Tuple
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import BigInteger, String, Column
from dotenv import load_dotenv
import logging

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///users.db")  # fallback на SQLite

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True)
    username = Column(String)
    city = Column(String)
    city_id = Column(String)


class Database:
    def __init__(self):
        Base.metadata.create_all(bind=engine)

    def save_user_city(self, user_id: int, username: str, city: str, city_id: Optional[str] = None):
        session: Session = SessionLocal()
        try:
            user = session.get(User, user_id)
            if user:
                user.username = username or "anonymous"
                user.city = city
                user.city_id = city_id
            else:
                user = User(
                    user_id=user_id,
                    username=username or "anonymous",
                    city=city,
                    city_id=city_id
                )
                session.add(user)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Ошибка при сохранении пользователя: {e}", exc_info=True)
        finally:
            session.close()
    def close(self):
        engine.dispose()

    def get_user_city(self, user_id: int) -> Optional[Tuple[Optional[str], Optional[str]]]:
        session: Session = SessionLocal()
        try:
            user = session.get(User, user_id)
            if user:
                return user.city, user.city_id
            return None
        except SQLAlchemyError as e:
            logging.error(f"Ошибка при получении города: {e}", exc_info=True)
            return None
        finally:
            session.close()

db = Database()
