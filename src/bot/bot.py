from __future__ import annotations

import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

dp = Dispatcher()


@dp.message(F.text)
async def handle_text(message: Message) -> None:
    # In prod this message should be forwarded to parsing/DB pipeline.
    await message.answer("Принято ✅")


async def run_bot() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is required")
    bot = Bot(BOT_TOKEN)
    await dp.start_polling(bot)
