import re

from aiogram import types
from aiogram.dispatcher.filters import Command
from datetime import datetime as dt

from data.config import ADMINS
from filters import IsPrivate
from loader import dp, db, bot


@dp.message_handler(IsPrivate(), text="Linkni o'chirish")
async def delete_write_link(message: types.Message):
    await message.answer("ℹ️ Linkni o'chirish uchun linkning id sini quyidagi ko'rinishda botga yuboring:\n\n<code>/delete_link link_id</code>")


@dp.message_handler(IsPrivate(), text="Link qo'shish")
async def add_write_link(message: types.Message):
    await message.answer("ℹ️ Oq ro'yhatga qo'shmoqchi bo'lgan link'ni quyidagi ko'rinishda botga yuboring:\n\n<code>/add_link ixtiyoriy_link</code>")


@dp.message_handler(IsPrivate(), text="Linklarni ko'rish")
async def show_write_link(message: types.Message):
    print("link show")
    data = await db.select_all_write_links()
    text = "🔗Jo'natish mumkin bo'lgan linklar:\n\nid | link -> kim qo'shgan\n"
    for item in data:
        text += f"{item.get('id')} | {item.get('link')} -> {item.get('added_by')}\n"
    await message.answer(text)


@dp.message_handler(IsPrivate(),text="Ban userlar")
async def show_block_user(message: types.Message):
    data = await db.select_all_black_user_list()
    text = 'Ban qilingan userlar:\n\n№| telegram id -> full name\n\n'
    for ind, item in enumerate(data):
        text += f"{ind+1}| {item.get('telegram_id')} -> {item.get('full_name')}\n"
    await message.answer(text)


@dp.message_handler(IsPrivate(),text="Ban'ni olib tashlash")
async def unban_block_user(message: types.Message):
    await message.answer("Quyidagi ko'rinishda ban'ni olib tashlamoqchi bo'lgan userning telegram id'sini <b>guruhga</b> jo'nating:\n\n<code>/unban telegram_id</code>")


# @dp.message_handler(text_contains="/unban")
# async def unban_block_user(message: types.Message):
#     chat_ids = bot.get_chat
#     print(message.text)
#     block_user_id = (message.text).split(' ')[1]
#     block_user = db.select_black_user(telegram_id=block_user_id)
#     if not block_user_id:
#         await message.answer("⚡Bu user ban olmagan!")
#         return 
#     await message.chat.unban(user_id=block_user_id)
#     await bot.unban_chat_member(chat_id=) 
#     await db.delete_black_user(telegram_id=block_user_id)
#     await message.answer(f"✅Foydalanuvchi {block_user.get('full_name')} bandan chiqarildi")


@dp.message_handler(Command("add_link", prefixes="!/"), IsPrivate())
async def unban(message: types.Message):
    m_split = (message.text).split(' ')
    if not len(m_split) == 2:
        await message.answer("❌Yuborishda xatolik!")
        return

    write_link = m_split[1]
    print(write_link)
    await db.add_write_link_list(
        link=write_link,
        added_by=message.from_user.full_name,
        created_at=dt.now()
    )
    await message.answer("✅ Link qo'shildi.")


@dp.message_handler(Command("delete_link", prefixes="!/"), IsPrivate())
async def delete_write_link(message: types.Message):
    command_parse = re.match(r'^\/delete_link\s+(\d+)$', message.text)
    if not command_parse:
        await message.answer("❌ Yuborishda xatolik!")
        return
    
    link_id = int((message.text).split(' ')[1])
    link = await db.select_write_link(id=link_id)
    if not link:
        await message.answer(f"❌ Bu id'ga ega bo'lgan link mavjud emas!")
        return 

    await db.delete_write_link(link_id=link_id)
    await message.answer("✅ Link o'chirib yuborildi.")
