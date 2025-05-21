import asyncio
import logging

from emoji import EMOJI_DATA
from aiogram import Router, F
from aiogram.types import Message
from database import db
from weather_api import fetch_weather

router = Router()

# Функция форматирования погоды
async def format_weather(weather: dict) -> str:
    wind_m_s = round(weather['current']['wind_kph'] / 3.6, 1)
    return (
        f"🌤 Погода в <b>{weather['location']['name']}</b>:\n"
        f"• 🌡 Температура: <b>{weather['current']['temp_c']}°C</b>\n"
        f"• 🤔 Ощущается как: <b>{weather['current']['feelslike_c']}°C</b>\n"
        f"• 💨 Ветер: <b>{wind_m_s} м/с</b>\n"
        f"• 💧 Влажность: <b>{weather['current']['humidity']}%</b>\n"
        f"• ☁️ Состояние: <b>{weather['current']['condition']['text']}</b>"
    )

# Функция вывода погоды
async def show_weather(user_id: int, message: Message):
    user_city = db.get_user_city(user_id)

    if not user_city or not user_city[0]:
        await message.answer("❌ Сначала укажи город через кнопку 'поменять что-то в жизни'")
        return

    weather = await fetch_weather(city=user_city[0], city_id=user_city[1])

    if not weather:
        await message.answer("⚠️ Не удалось получить данные. Попробуй позже")
        return

    text = await format_weather(weather)
    await message.answer(text, parse_mode="HTML")

# Хэндлер на кнопку "чо по погоде"
@router.message(F.text == '👀Чо по погоде ?')
async def handle_weather(message: Message):
    await show_weather(message.from_user.id, message)

# Хэндлер на кнопку "чо по городу"
@router.message(F.text == 'чо по городу 🤌🏻')
async def show_city(message: Message):
    user_city = db.get_user_city(message.from_user.id)

    await message.answer(
        f"📍Ты че забыл? {user_city[0]} 🤭"
        if user_city and user_city[0]
        else "❌ Город не установлен. Нажми 'поменять что-то в жизни'"
    )

# --- Хэндлеры медиа
@router.message(F.photo)
async def handle_photo(message: Message):
    await message.answer('Зачем ты мне это отправляешь? 🤡')
    await asyncio.sleep(4)
    await message.answer_photo(
        message.photo[-1].file_id,
        reply_to_message_id=message.message_id,
        caption='Держи обратно твою хуячку 🥱',
    )

@router.message(F.sticker)
async def handle_sticker(message: Message):
    first_msg = await message.answer('Я не понимаю зачем ты мне отправляешь это ? 😐')
    await asyncio.sleep(5)
    await first_msg.edit_text("нате 🫡")
    await message.answer_sticker(
        message.sticker.file_id,
        reply_to_message_id=message.message_id
    )

@router.message(F.text)
async def handle_text(message: Message):
    text = message.text
    if any(char in EMOJI_DATA for char in text):
        first_msg = await message.answer("Я не понимаю, тебе смешно что ли?")
        await asyncio.sleep(2)
        await first_msg.edit_text(f"Держи свою эмодзи назад", parse_mode=None)
        await asyncio.sleep(1)
        emojis = "".join(c for c in text if c in EMOJI_DATA)
        await message.answer(emojis)
        await message.delete()
    else:
        await message.answer("Зачем ты со мной говоришь?👀\nЯ по погоде двигаюсь, очнись 🐴")

@router.message(F.voice)
async def handle_voice(message: Message):
    await asyncio.sleep(2)
    await message.delete()
    await message.answer("Ало, чел!\nя могу подсказать чо по погоде, но я плохой собеседник")
    await asyncio.sleep(6)
    await message.answer('Не.. ну ты внатуре придумал хорошо\nОбщаться с ботом 🤡')