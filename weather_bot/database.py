import sqlite3
import logging
from typing import Optional, Tuple

class Database:
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    city TEXT,
                    city_id TEXT
                )
            """)
            conn.commit()

    def _get_connection(self):
        """Возвращает соединение с БД."""
        return sqlite3.connect(self.db_path)

    def save_user_city(self, user_id: int, username: str, city: str, city_id: Optional[str] = None):
        """Сохраняет/обновляет город пользователя."""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """INSERT OR REPLACE INTO users 
                    (user_id, username, city, city_id) 
                    VALUES (?, ?, ?, ?)""",
                    (user_id, username or "anonymous", city, city_id)
                )
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Ошибка БД: {e}", exc_info=True)

    def get_user_city(self, user_id: int) -> Optional[Tuple[str, str]]:
        """Возвращает город и city_id пользователя."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT city, city_id FROM users WHERE user_id = ?", (user_id,))
                return cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Ошибка БД: {e}", exc_info=True)
            return None

db = Database()