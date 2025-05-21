import asyncio
import logging
import os

import colorlog
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import routers
from database import db

def setup_logging():
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))
    logging.basicConfig(level=logging.INFO, handlers=[handler])


async def main():
    setup_logging()
    load_dotenv()
    logger = logging.getLogger(__name__)

    BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    for router in routers:
        dp.include_router(router)

    try:
        logger.info("Ребята мы разгоняемся 🚁")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}", exc_info=True)
    finally:
        logger.info(">>> [SHUTDOWN] Завершаем работу...")
        await bot.session.close()
        db.close()
        logger.info(">>> [SHUTDOWN] Готово!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info(">>> Прерывание с клавиатуры (Ctrl+C)")
    except Exception as e:
        logging.critical(f"Необработанная ошибка: {e}", exc_info=True)
