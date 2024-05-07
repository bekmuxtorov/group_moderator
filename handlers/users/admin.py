import re
from datetime import datetime as dt

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext

from loader import dp, db, bot
from data.config import ADMINS, add_admin_id
from filters import IsPrivate, IsBotAdmin
from states.add_admin import AddAdmin


@dp.message_handler(IsPrivate(), IsBotAdmin(), text="🔗Linkni o'chirish")
async def delete_write_link(message: types.Message):
    await message.answer("ℹ️ Linkni o'chirish uchun linkning id sini quyidagi ko'rinishda botga yuboring:\n\n<code>/delete_link link_id</code>")


@dp.message_handler(IsPrivate(), IsBotAdmin(), text="➕Link qo'shish")
async def add_write_link(message: types.Message):
    await message.answer("ℹ️ Oq ro'yhatga qo'shmoqchi bo'lgan link'ni quyidagi ko'rinishda botga yuboring:\n\n<code>/add_link ixtiyoriy_link</code>")


@dp.message_handler(IsPrivate(), IsBotAdmin(), text="🔗Linklarni ko'rish")
async def show_write_link(message: types.Message):
    data = await db.select_all_write_links()
    text = "🔗Jo'natish mumkin bo'lgan linklar:\n\nid | link -> kim qo'shgan\n"
    for item in data:
        text += f"<code>{item.get('id')}</code> | {item.get('link')} -> {item.get('added_by')}\n"
    await message.answer(text)


@dp.message_handler(IsPrivate(), IsBotAdmin(), text="👤Ban userlar")
async def show_block_user(message: types.Message):
    data = await db.select_all_black_user_list()
    text = 'Ban qilingan userlar:\n\n№| telegram id -> full name\n\n'
    for ind, item in enumerate(data):
        text += f"{ind+1}| <code>{item.get('telegram_id')}</code> -> {item.get('full_name')}\n"
        if (ind % 40 == 0) and (ind != 0):
            await message.answer(text)
            text = ''

    if text:
        await message.answer(text)


@dp.message_handler(IsPrivate(), IsBotAdmin(), text="👤Ban'ni olib tashlash")
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


@dp.message_handler(Command("add_link", prefixes="!/"), IsPrivate(), IsBotAdmin())
async def unban(message: types.Message):
    m_split = (message.text).split(' ')
    if not len(m_split) == 2:
        await message.answer("❌Yuborishda xatolik!")
        return

    write_link = m_split[1]
    await db.add_write_link_list(
        link=write_link,
        added_by=message.from_user.full_name,
        created_at=dt.now()
    )
    await message.answer("✅ Link qo'shildi.")


@dp.message_handler(Command("delete_link", prefixes="!/"), IsPrivate(), IsBotAdmin())
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


@dp.message_handler(IsPrivate(), IsBotAdmin(), text="💡Botga admin qo'shish")
async def add_admin(message: types.Message):
    # await message.answer("Botga admin qo'shish uchun, qo'shmoqchi bo'lgan userning ixtiyoriy xabarini botga forward qiling: ")
    await message.answer("➕ Qo'shmoqchi bo'lgan adminni telegram id sini kiriting:")
    await AddAdmin.admin_id.set()


@dp.message_handler(IsPrivate(), IsBotAdmin(), state=AddAdmin.admin_id)
async def add_admin(message: types.Message, state: FSMContext):
    if not (message.text).isdigit():
        await message.answer("❌ Yuborishda xatolik!")
        await state.finish()
        return

    add_admin_id(telegram_id=message.text)
    try:
        await db.add_admin(telegram_id=int(message.text), full_name=message.from_user.full_name, created_at=dt.now())
    except:
        pass
    await message.answer("✅ Admin qo'shildi.")
    await state.finish()
