from __future__ import annotations

import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

from src.db.models import RawMessage
from src.db.session import SessionLocal

BOT_TOKEN = os.getenv("BOT_TOKEN", "")


dp = Dispatcher()


@dp.message(F.text)
async def handle_text(message: Message) -> None:
    trader_id = int(message.from_user.id)
    with SessionLocal() as db:
        db.add(
            RawMessage(
                trader_id=trader_id,
                chat_id=int(message.chat.id),
                message_id=int(message.message_id),
                text=message.text or "",
            )
        )
        db.commit()
    await message.answer("Принято ✅")


async def run_bot() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is required")
    bot = Bot(BOT_TOKEN)
    await dp.start_polling(bot)
