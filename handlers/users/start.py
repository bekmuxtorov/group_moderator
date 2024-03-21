from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp, db, bot
from data.config import ADMINS
from keyboards.default.default_buttons import make_buttons
from filters import IsAdmin, IsPrivate, IsBotAdmin


@dp.message_handler(IsPrivate(), IsBotAdmin(), CommandStart())
async def bot_start(message: types.Message):
    await message.answer("Admin uchun menyu:", reply_markup=make_buttons(["👤Ban userlar", "🔗Linklarni ko'rish", "👤Ban'ni olib tashlash", "➕Link qo'shish", "💡Botga admin qo'shish", "🔗Linkni o'chirish", "📝Foydalanish uchun qo'llanma"], row_width=2))


@dp.message_handler(IsPrivate(), CommandStart())
async def bot_start(message: types.Message):
    await message.answer("✅ Himmat 700+ loyihasining guruhlarini nazorat qiluvchi bot!\n\nBotdan faqat adminlar foydalanishi mumkin.")


@dp.message_handler(IsPrivate(), IsBotAdmin(), text="📝Foydalanish uchun qo'llanma")
async def bot_start(message: types.Message):
    await message.answer("💡 Qo'llanma uchun link: \n\nhttps://telegra.ph/Himmat-nazoratchi-botidan-foydalanish-uchun-qollanma-03-21")
