import asyncio
import logging
import colorlog
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from my_handlers import router
from database import db


# Настройка цвЯтного логирования
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

#  Глобально создаём bot — чтобы потом в shutdown его закрыть (уебать)
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)
storage = MemoryStorage()

#  graceful_shutdown_функция
async def shutdown():
    logging.info(">>> [SHUTDOWN] Закрываем ресурсы...")
    await bot.session.close()
    db.close()
    logging.info(">>> [SHUTDOWN] Готово!")

def get_shutdown_handler(bot: Bot, dp: Dispatcher):
    async def shutdown():
        logging.info(">>> [SHUTDOWN] Завершаем работу бота...")
        await bot.session.close()
        db.close()
        logging.info(">>> [SHUTDOWN] Куда ты там разгоняешься? ✋🏻")
    return shutdown

# Точка входа
async def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        logger.info("Ребята мы разгоняемся 🚁")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}", exc_info=True)
    finally:
        await shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info(">>> Прерывание с клавиатуры (Ctrl+C)")
    except Exception as e:
        logging.critical(f"Необработанная ошибка: {e}", exc_info=True)