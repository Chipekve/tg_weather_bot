import sqlite3
import logging
from typing import Optional, Tuple

class Database:
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        try:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    city TEXT,
                    city_id TEXT
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Ошибка при инициализации БД: {e}", exc_info=True)

    def save_user_city(self, user_id: int, username: str, city: str, city_id: Optional[str] = None):
        try:
            self.conn.execute(
                """INSERT OR REPLACE INTO users 
                (user_id, username, city, city_id) 
                VALUES (?, ?, ?, ?)""",
                (user_id, username or "anonymous", city, city_id)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Ошибка БД при сохранении: {e}", exc_info=True)

    def get_user_city(self, user_id: int) -> Optional[Tuple[Optional[str], Optional[str]]]:
        try:
            cursor = self.conn.execute(
                "SELECT city, city_id FROM users WHERE user_id = ?", (user_id,))
            return cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Ошибка БД при получении города: {e}", exc_info=True)
            return None

    def close(self):
        try:
            self.conn.close()
        except Exception as e:
            logging.error(f"Ошибка при закрытии БД: {e}", exc_info=True)

db = Database()