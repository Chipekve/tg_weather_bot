import asyncio
import logging

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from weather_api import search_cities
from keyboards import cities_keyboard
from database import db
from .weather import show_weather

router = Router()

class UserState(StatesGroup):
    changing_city = State()

# Начинаем процесс смены города — просим ввести название
@router.message(F.text == 'поменять что-то в жизни')
async def start_city_change(message: Message, state: FSMContext):
    msg = await message.answer("📝 Введи название города:")
    await state.update_data(temp_msg_id=msg.message_id)
    await state.set_state(UserState.changing_city)

# Обработка ввода города — ищем варианты, показываем кнопки
@router.message(UserState.changing_city)
async def process_city(message: Message, state: FSMContext, bot: Bot):
    state_data = await state.get_data()
    temp_msg_id = state_data.get('temp_msg_id')
    if temp_msg_id:
        try:
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=temp_msg_id,
                text="🔍 Ищу варианты..."
            )
        except:
            new_msg = await message.answer("🔍 Ищу варианты...")
            temp_msg_id = new_msg.message_id

    city_query = message.text.strip()
    cities = await search_cities(city_query)

    if not cities:
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=temp_msg_id,
            text="⚠️ Города не найдены. Попробуй еще раз:"
        )
        return

    keyboard = cities_keyboard(cities)
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=temp_msg_id,
        text="🔍 Выбери точный город из списка:",
        reply_markup=keyboard
    )
    await state.update_data(cities=cities)

# Обработка выбора города из списка кнопок
@router.callback_query(F.data.startswith("city_"))
async def handle_city_selection(callback: CallbackQuery, state: FSMContext):
    try:
        city_id = callback.data.split("_")[1]
        user_id = callback.from_user.id

        state_data = await state.get_data()
        cities = state_data.get("cities")
        if not cities:
            return await callback.answer("❌ Сессия истекла", show_alert=True)

        selected_city = next(
            (city for city in cities if str(city.get('id')) == city_id),
            None
        )
        if not selected_city:
            return await callback.answer("❌ Ошибка выбора", show_alert=True)

        db.save_user_city(
            user_id=user_id,
            username=callback.from_user.username,
            city=selected_city['name'],
            city_id=city_id
        )

        await callback.message.edit_text(f"✅ {selected_city['name']} я это запишу 👀✍️")
        await asyncio.sleep(1)
        await callback.message.delete()

        await show_weather(callback.from_user.id, callback.message)

        await state.clear()
        await callback.answer()

    except Exception as e:
        logging.error(f"City selection error: {e}", exc_info=True)
        await callback.answer("⚠️ Ошибка сервера", show_alert=True)

# Обработка переключения страниц для городов при выборе
@router.callback_query(F.data.startswith("page_"))
async def handle_pagination(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split("_")[1])
    state_data = await state.get_data()
    cities = state_data.get("cities")
    if not cities:
        return await callback.answer("❌ Сессия истекла", show_alert=True)

    from keyboards import cities_keyboard
    keyboard = cities_keyboard(cities, page=page)
    try:
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        await callback.answer()
    except Exception as e:
        logging.error(f"Pagination error: {e}", exc_info=True)
        await callback.answer("⚠️ Ошибка сервера", show_alert=True)
