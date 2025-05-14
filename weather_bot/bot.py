import asyncio
import logging
import colorlog

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from my_handlers import router
from database import db


# Настройка логирования
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
    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler]
    )

#  точка входа
async def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        logger.info("Ребята мы разгоняемся 🚁")

        bot = Bot(token=BOT_TOKEN)
        dp = Dispatcher(storage=MemoryStorage())
        dp.include_router(router)

        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}", exc_info=True)
    finally:
        logger.info("Какая нахуй разгоняемся ?🤡")
        if 'bot' in locals():
            await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Какая нахуй разгоняемся ?🤡")
    except Exception as e:
        logging.critical(f"Необработанная ошибка: {e}", exc_info=True)