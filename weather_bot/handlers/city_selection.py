import asyncio
import logging

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from weather_api import search_cities
from keyboards import cities_keyboard, cancel_city_change_keyboard, BTN_CHANGE_CITY, BTN_CITY, BTN_FORECAST, BTN_WEATHER
from database import db
from .weather import show_weather, show_city, handle_3day_forecast


router = Router()


class UserState(StatesGroup):
    changing_city = State()


# Начинаем процесс смены города — просим ввести название
@router.message(F.text == BTN_CHANGE_CITY)
async def start_city_change(message: Message, state: FSMContext, bot: Bot):
    state_data = await state.get_data()
    old_msg_id = state_data.get("temp_msg_id")
    old_button_id = state_data.get("button_msg_id")

    if old_msg_id and await state.get_state() == UserState.changing_city:
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=old_msg_id)
        except:
            pass

    if old_button_id:
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=old_button_id)
        except:
            pass

    await state.update_data(
        button_msg_id=message.message_id,
        temp_msg_id=None
    )
    await state.set_state(UserState.changing_city)

    msg = await message.answer(
        "📝 Введи название города:",
        reply_markup=cancel_city_change_keyboard()
    )
    await state.update_data(temp_msg_id=msg.message_id)


@router.callback_query(F.data == "cancel_city_change")
async def cancel_city_change(callback: CallbackQuery, state: FSMContext):
    await callback.answer("GG )")
    data = await state.get_data()
    chat_id = callback.message.chat.id
    bot = callback.bot

    temp_msg_id = data.get("temp_msg_id")
    button_msg_id = data.get("button_msg_id")

    try:
        await callback.message.edit_text("🚫 Смена города отменена.", reply_markup=None)
    except:
        pass

    await asyncio.sleep(2)

    if temp_msg_id:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=temp_msg_id)
        except:
            pass

    if button_msg_id and button_msg_id != callback.message.message_id:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=button_msg_id)
        except:
            pass

    try:
        await callback.message.delete()
    except:
        pass

    await state.clear()


# Обработка ввода города — ищем варианты, показываем кнопки
@router.message(UserState.changing_city)
async def process_city(message: Message, state: FSMContext, bot: Bot):
    INTERRUPT_BUTTONS = {
        BTN_WEATHER: "show_weather",
        BTN_CITY: "show_city",
        BTN_FORECAST: "handle_3day_forecast",
    }

    if message.text in INTERRUPT_BUTTONS:
        state_data = await state.get_data()
        old_msg_id = state_data.get("temp_msg_id")
        old_button_id = state_data.get("button_msg_id")
        await message.answer("Смена города прервана.")

        for msg_id in [old_msg_id, old_button_id]:
            if msg_id:
                try:
                    await bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
                except:
                    pass

        await state.clear()

        handler_name = INTERRUPT_BUTTONS[message.text]

        if handler_name == "show_weather":
            await show_weather(message.from_user.id, message)
        elif handler_name == "show_city":
            await show_city(message)
        elif handler_name == "handle_3day_forecast":
            await handle_3day_forecast(message)
        return

    state_data = await state.get_data()
    temp_msg_id = state_data.get("temp_msg_id")
    if temp_msg_id:
        try:
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=temp_msg_id,
                text="🔍 Ищу варианты...",
            )
        except:
            new_msg = await message.answer("🔍 Ищу варианты...")
            temp_msg_id = new_msg.message_id
            await state.update_data(temp_msg_id=temp_msg_id)

    city_query = message.text.strip()
    cities = await search_cities(city_query)

    if not cities:
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=temp_msg_id,
            text="⚠️ Города не найдены. Попробуй еще раз:",
        )
        return

    keyboard = cities_keyboard(cities)
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=temp_msg_id,
        text="🔍 Выбери точный город из списка:",
        reply_markup=keyboard,
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
            (city for city in cities if str(city.get("id")) == city_id), None
        )
        if not selected_city:
            return await callback.answer("❌ Ошибка выбора", show_alert=True)

        db.save_user_city(
            telegram_id=user_id,
            username=callback.from_user.username,
            city=selected_city["name"],
            city_id=city_id,
        )

        await callback.message.edit_text(f"✅ {selected_city['name']} я это запишу 👀✍️")
        await asyncio.sleep(1)
        await callback.message.delete()

        await show_weather(callback.from_user.id, callback.message)

        await state.clear()
        await callback.answer("GG")

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

    keyboard = cities_keyboard(cities, page=page)
    try:
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        await callback.answer("GG")
    except Exception as e:
        logging.error(f"Pagination error: {e}", exc_info=True)
        await callback.answer("⚠️ Ошибка сервера", show_alert=True)