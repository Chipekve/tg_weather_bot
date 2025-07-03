from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message
import time

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit=1.5):
        super().__init__()
        self.rate_limit = rate_limit
        self.last_time = {}

    async def __call__(self, handler, event, data):
        if isinstance(event, Message):
            user_id = event.from_user.id
            now = time.monotonic()
            last = self.last_time.get(user_id, 0)
            if now - last < self.rate_limit:
                # Просто игнорируем сообщение, не обрабатываем его
                return
            self.last_time[user_id] = now
        return await handler(event, data) 