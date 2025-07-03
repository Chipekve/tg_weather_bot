import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from keyboards import get_reply_menu
from database import db

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    user = await asyncio.to_thread(db.get_user_by_id, telegram_id=user_id)

    if not user:
        await asyncio.to_thread(db.add_user, telegram_id=user_id, username=username)

    is_subscribed = user.is_subscribed if user else False
    try:
        await message.answer_photo(
            photo="https://i.imgur.com/3L2Pliv.png",
            caption="Добро пожаловать! 👋\nвыбирай чо по кайфу 🤌🏻\n\nВыбирай действие:",
            reply_markup=get_reply_menu(is_subscribed),
        )
    except Exception:
        await message.answer(
            "Добро пожаловать! 👋\nвыбирай чо по кайфу 🤌🏻\n\nВыбирай действие:",
            reply_markup=get_reply_menu(is_subscribed),
        )


@router.message(F.text.in_({"📬 Включить автосообщения", "🔕 Выключить автосообщения"}))
async def toggle_subscription_handler(message: Message):
    user_id = message.from_user.id

    new_status = await asyncio.to_thread(db.toggle_subscription, telegram_id=user_id)

    if new_status is None:
        await message.answer("⚠️ Не удалось обновить подписку.")
        return

    status_text = (
        "✅ Вы подписались на автосообщения"
        if new_status
        else "❌ Вы отписались от автосообщений"
    )
    await message.answer(status_text, reply_markup=get_reply_menu(new_status))
