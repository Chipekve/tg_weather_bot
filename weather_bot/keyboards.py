from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict

# --- reply кнопкА
def get_reply_menu():
    keyboard = [
        [KeyboardButton(text='👀Чо по погоде ?')],
        [KeyboardButton(text='чо по городу 🤌🏻'), KeyboardButton(text='поменять что-то в жизни')]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=False)

#  Инлайн кнопкА
CITIES_PER_PAGE = 2
def cities_keyboard(cities: List[Dict[str, str]], page: int = 0, per_page: int = CITIES_PER_PAGE):
    start_idx = page * per_page
    end_idx = start_idx + per_page
    current_cities = cities[start_idx:end_idx]

    buttons = [
        [InlineKeyboardButton(text=f"{city['name']}, {city['country']}", callback_data=f"city_{city['id']}")]
        for city in current_cities
    ]

    # Пагинация (если нужно)
    pagination = []
    if page > 0:
        pagination.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"page_{page - 1}"))
    if end_idx < len(cities):
        pagination.append(InlineKeyboardButton(text="▶️ Вперед", callback_data=f"page_{page + 1}"))

    if pagination:
        buttons.append(pagination)

    return InlineKeyboardMarkup(inline_keyboard=buttons)