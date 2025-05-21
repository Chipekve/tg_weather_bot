from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from keyboards import get_reply_menu

router = Router()

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
