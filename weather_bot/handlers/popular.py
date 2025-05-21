import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from weather_api import fetch_weather
from keyboards import get_popular_cities_keyboard
from .weather import format_weather

router = Router()

# Обработка нажатия кнопки "Популярные города"
@router.message(F.text == "Популярные города")
async def handle_popular_cities(message: Message):
    keyboard = get_popular_cities_keyboard(page=0)
    await message.answer("📍 Выбери популярный город:", reply_markup=keyboard)

# Обработка переключения страниц популярных городов
@router.callback_query(F.data.startswith("popular_page_"))
async def handle_popular_page(callback: CallbackQuery):
    try:
        page = int(callback.data.split("_")[2])
        keyboard = get_popular_cities_keyboard(page)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        await callback.answer()
    except Exception as e:
        logging.error(f"Popular pagination error: {e}", exc_info=True)
        await callback.answer("⚠️ Ошибка при переключении страниц", show_alert=True)

# Обработка нажатия на конкретный популярный город
@router.callback_query(F.data.startswith("popular_city_"))
async def handle_popular_city(callback: CallbackQuery):
    try:
        city_name = callback.data[len("popular_city_"):]
        weather = await fetch_weather(city=city_name)

        if not weather:
            return await callback.answer("⚠️ Не удалось получить погоду", show_alert=True)

        # Вставляй сюда функцию форматирования погоды из weather.py, если надо
        text = await format_weather(weather)

        await callback.message.edit_text(text, parse_mode="HTML")
        await callback.answer()
    except Exception as e:
        logging.error(f"Popular city weather error: {e}", exc_info=True)
        await callback.answer("⚠️ Ошибка сервера", show_alert=True)
