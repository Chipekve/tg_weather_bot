import asyncio
import aiohttp
import logging

from emoji import EMOJI_DATA
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Bot

from config import WEATHER_API_KEY
from keyboards import get_reply_menu, cities_keyboard
from database import db

router = Router()

class UserState(StatesGroup):
    changing_city = State()

# в fetch_weather и search_cities добавлены retry-декораторы
# для устойчивости и логика защиты от сбоев API запросов
async def fetch_weather(city: str = None, city_id: str = None, retries: int = 3) -> dict | None:
    if not city and not city_id:
        return None

    params = {
        "key": WEATHER_API_KEY,
        "lang": "ru",
        "q": f"id:{city_id}" if city_id else city
    }

    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "http://api.weatherapi.com/v1/current.json",
                    params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    logging.warning(f"WeatherAPI returned status {response.status}")
        except Exception as e:
            logging.error(f"Weather API error on attempt {attempt + 1}: {e}")

        await asyncio.sleep(1)

    return None

async def search_cities(query: str, retries: int = 3) -> list | None:
    if len(query) < 2:
        return None

    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "http://api.weatherapi.com/v1/search.json",
                    params={"key": WEATHER_API_KEY, "q": query}
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    logging.warning(f"City search failed with status {response.status}")
        except Exception as e:
            logging.error(f"City search error on attempt {attempt + 1}: {e}")

        await asyncio.sleep(1)

    return None


# --- Хэндлеры / роутеры
@router.message(Command("start"))
async def cmd_start(message: Message):
    try:
        await message.answer_photo(
            photo="https://i.imgur.com/3L2Pliv.png",
            caption="Добро пожаловать! 👋\nвыбирай чо по кайфу 🤌🏻\n\nВыбирай действие:",
            reply_markup=get_reply_menu()
        )
    except Exception:
        await message.answer(
            "Добро пожаловать! 👋\nвыбирай чо по кайфу 🤌🏻\n\nВыбирай действие:",
            reply_markup=get_reply_menu()
        )

#  тута функция на вывод погоды в формате
async def show_weather(user_id: int, message: Message):

    user_city = db.get_user_city(user_id)
    if not user_city or not user_city[0]:
        await message.answer("❌ Сначала укажи город через кнопку 'поменять что-то в жизни'")
        return

    weather = await fetch_weather(city=user_city[0], city_id=user_city[1])

    if not weather:
        await message.answer("⚠️ Не удалось получить данные. Попробуй позже")
        return

    wind_m_s = round(weather['current']['wind_kph'] / 3.6, 1)
    await message.answer(
        f"🌤 Погода в {weather['location']['name']}:\n"
        f"• 🌡 Температура: {weather['current']['temp_c']}°C\n"
        f"• 🤔 Ощущается как: {weather['current']['feelslike_c']}°C\n"
        f"• 💨 Ветер: {wind_m_s} м/с\n"
        f"• 💧 Влажность: {weather['current']['humidity']}%\n"
        f"• ☁️ Состояние: {weather['current']['condition']['text']}"
    )

#  Magic фильтр на кнопку чо по погоде
@router.message(F.text == '🤌🏻 Чо по погоде ?')
async def handle_weather(message: Message):
    await show_weather(message.from_user.id, message)

#  Magic фильтр на кнопку город
@router.message(F.text == 'чо по городу 🤌🏻')
async def show_city(message: Message):
    user_city = db.get_user_city(message.from_user.id)
    await message.answer(
        f"📍Ты че забыл? {user_city[0]} 🤭"
        if user_city and user_city[0]
        else "❌ Город не установлен. Нажми 'поменять что-то в жизни'"
    )

#  Magic фильтр на... короче понятно уже на что 🤡
@router.message(F.text == 'поменять что-то в жизни')
async def start_city_change(message: Message, state: FSMContext):
    msg = await message.answer("📝 Введи название города:")
    await state.update_data(temp_msg_id=msg.message_id)
    await state.set_state(UserState.changing_city)

#  тут конечно сложная штука, функция в роутере на изменение города и т/д
@router.message(UserState.changing_city)
async def process_city(message: Message, state: FSMContext, bot: Bot):
    state_data = await state.get_data()
    temp_msg_id = state_data.get('temp_msg_id')

    #  Меняем текст
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
    #  тут подставляем инлайн кнопки с вариантами городов
    keyboard = cities_keyboard(cities)

    #  Заменяем "Ищем варианты..." на сообщение с кнопками
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=temp_msg_id,
        text="🔍 Выбери точный город из списка:",
        reply_markup=keyboard
    )

    await state.update_data(cities=cities)
    # await state.clear()

#  Обработка выбора города из списка
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

        db.save_user_city(  # Используем метод из db
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

#  наконец-то обработчик для пагинации, нормально заработает
@router.callback_query(F.data.startswith("page_"))
async def handle_pagination(callback: CallbackQuery, state: FSMContext):
    # Логика обработки переключения страниц списка городов
    page = int(callback.data.split("_")[1])
    state_data = await state.get_data()
    cities = state_data.get("cities")
    if not cities:
        return await callback.answer("❌ Сессия истекла", show_alert=True)

    keyboard = cities_keyboard(cities, page=page)
    try:
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        await callback.answer()
    except Exception as e:
        logging.error(f"Pagination error: {e}", exc_info=True)
        await callback.answer("⚠️ Ошибка сервера", show_alert=True)


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