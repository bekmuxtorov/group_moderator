from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp, db, bot
from data.config import ADMINS
from keyboards.default.default_buttons import make_buttons
from filters import IsAdmin, IsPrivate


@dp.message_handler(IsPrivate(), CommandStart())
async def bot_start(message: types.Message):
    await message.answer("Admin uchun menyu:", reply_markup=make_buttons(["Ban userlar","Ban'ni olib tashlash", "Linklarni ko'rish", "Link qo'shish", "Linkni o'chirish"]))
