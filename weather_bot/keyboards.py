from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from popular_cities import POPULAR_CITIES, POPULAR_PAGE
from typing import List, Dict

# --- reply кнопкА
def get_reply_menu():
    keyboard = [
        [KeyboardButton(text='поменять что-то в жизни'), KeyboardButton(text='👀Чо по погоде ?')],
        [KeyboardButton(text='чо по городу 🤌🏻'), KeyboardButton(text='Популярные города')],
        [KeyboardButton(text='прогноз на 3 дня')]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=False)

#  Инлайн кнопкА
def get_popular_cities_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    start_idx = page * POPULAR_PAGE
    end_idx = start_idx + POPULAR_PAGE
    current_cities = POPULAR_CITIES[start_idx:end_idx]

    buttons = [
        [InlineKeyboardButton(text=city, callback_data=f"popular_city_{city}")]
        for city in current_cities
    ]

    pagination = []
    if page > 0:
        pagination.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"popular_page_{page - 1}"))
    if end_idx < len(POPULAR_CITIES):
        pagination.append(InlineKeyboardButton(text="▶️ Вперед", callback_data=f"popular_page_{page + 1}"))

    if pagination:
        buttons.append(pagination)

    return InlineKeyboardMarkup(inline_keyboard=buttons)

CITIES_PER_PAGE = 2
def cities_keyboard(cities: List[Dict[str, str]], page: int = 0, per_page: int = CITIES_PER_PAGE):
    start_idx = page * per_page
    end_idx = start_idx + per_page
    current_cities = cities[start_idx:end_idx]

    buttons = [
        [InlineKeyboardButton(text=f"{city['name']}, {city['country']}", callback_data=f"city_{city['id']}")]
        for city in current_cities
    ]

    pagination_search = []
    if page > 0:
        pagination_search.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"page_{page - 1}"))
    if end_idx < len(cities):
        pagination_search.append(InlineKeyboardButton(text="▶️ Вперед", callback_data=f"page_{page + 1}"))

    if pagination_search:
        buttons.append(pagination_search)

    return InlineKeyboardMarkup(inline_keyboard=buttons)