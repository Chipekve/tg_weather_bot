import asyncio
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramForbiddenError, TelegramNotFound
from aiogram.fsm.storage.memory import MemoryStorage
import colorlog

from handlers import routers
from database import db, Database
from keyboards import get_reply_menu
from handlers.weather_sender import send_weather_to_subscribers


# Настройка цветного логгирования
def setup_logging() -> None:
    handler = colorlog.StreamHandler()
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )
    handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, handlers=[handler])


# Фоновая задача рассылки прогноза погоды
async def periodic_weather_task(bot: Bot, interval: int = 15) -> None:
    while True:
        await send_weather_to_subscribers(bot)
        await asyncio.sleep(interval)

async def broadcast_reply_keyboards(bot: Bot, db: Database):
    users = await asyncio.to_thread(db.get_all_users)

    for user in users:
        try:
            await bot.send_chat_action(user.telegram_id, action="typing")
            await bot.send_message(
                chat_id=user.telegram_id,
                text="клавиатура обновлена",
                reply_markup=get_reply_menu(user.is_subscribed),
            )
        except (TelegramForbiddenError, TelegramNotFound):
            logging.warning(f"Пользователь {user.telegram_id} недоступен.")
        except Exception as e:
            logging.error(f"Ошибка при рассылке клавиатуры: {e}", exc_info=True)

    logging.info("Обновление клавиатур завершено.")

async def main() -> None:
    setup_logging()
    load_dotenv()
    logger = logging.getLogger(__name__)

    BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
    if not BOT_TOKEN:
        logger.critical("❌ BOT_TOKEN не найден в переменных окружения.")
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    await broadcast_reply_keyboards(bot, db)

    # Регистрируем роутеры
    for router in routers:
        dp.include_router(router)

    asyncio.create_task(periodic_weather_task(bot))

    try:
        logger.info("Ребята мы разгоняемся 🚁")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.critical(f"❗ Критическая ошибка: {e}", exc_info=True)
    finally:
        logger.info("Куда ты разгоняешься? 🤡")
        await bot.session.close()
        db.close()
        logger.info("✅ все, стоим.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("⏹ Остановка с клавиатуры (Ctrl+C)")
    except Exception as e:
        logging.critical(f"❗ Необработанная ошибка: {e}", exc_info=True)
