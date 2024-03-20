import re
import asyncio
from datetime import datetime as dt

from aiogram.dispatcher.filters import Command
from aiogram import types

from data.config import ADMINS
from filters.is_admin import IsAdmin
from loader import dp, db, bot
from filters import IsGroup

MAX_ATTEMPT_FOR_BLOCK = 2

REGEXS = [r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+|www\.\S+', r'@\w+', r'https?:\/\/t\.me\/\+?[\w-]+']


@dp.message_handler(IsGroup(), content_types=types.ContentTypes.NEW_CHAT_MEMBERS)
async def ban(message: types.Message):
    text = f"""Assalomu alaykum {message.from_user.full_name}[<a href=\'tg://user?id={message.from_user.id}\'>{message.from_user.id}</a>].\n<b>Himmat 700+</b> loyihasining muhokama guruhiga xush kelibsiz!"""
    service_message = await message.answer(text)
    await asyncio.sleep(9)
    await bot.delete_message(chat_id=message.chat.id, message_id=service_message.message_id)
    await message.delete()


@dp.message_handler(IsGroup(), content_types=types.ContentTypes.LEFT_CHAT_MEMBER)
async def ban(message: types.Message):
    await message.delete()


@dp.message_handler(IsGroup(), Command("unban", prefixes="!/"), IsAdmin())
async def unban(message: types.Message):
    command_parse = re.match(r'^\/unban\s+(\d+)$', message.text)
    if not command_parse:
        return     

    member_id = int((message.text).split(' ')[1])
    chat_id = message.chat.id
    block_user = await db.select_black_user(telegram_id=member_id)
    if not block_user:
        service_message = await  message.answer("⚡Bu user ban olmagan!")
        await asyncio.sleep(5)
        await bot.delete_message(chat_id, message_id=service_message.message_id)
        await bot.delete_message(chat_id, message.message_id)
        return 

    await message.chat.unban(user_id=member_id, only_if_banned=True)
    await db.delete_black_user(telegram_id=member_id)
    service_message = await message.answer(f"Foydalanuvchi {block_user.get('full_name')} bandan chiqarildi!")
    await asyncio.sleep(6)
    await bot.delete_message(chat_id, service_message.message_id)
    await bot.delete_message(chat_id, message.message_id)


async def get_urls(text: str):
    urls = []
    for regex in REGEXS:
        urls += re.findall(regex, text)
    return urls


async def user_blocking(message: types.Message):
    user_id = message.from_user.id
    message_id = message.message_id
    chat_id = message.chat.id

    if user_id in [int(item) for item in ADMINS]:
        return 
    await message.chat.kick(user_id=user_id)
    await bot.delete_message(chat_id, message_id)
    service_message = await message.answer(f"Foydalanuvchi {message.from_user.full_name}[<a href=\'tg://user?id={message.from_user.id}\'>{message.from_user.id}</a>] guruhdan haydaldi.")
    await asyncio.sleep(5)
    await bot.delete_message(chat_id, service_message.message_id)
    return


@dp.message_handler(IsGroup(), content_types=types.ContentTypes.ANY)
async def ban(message: types.Message):
    if message.content_type in types.ContentTypes.PHOTO or \
    message.content_type in types.ContentTypes.VIDEO or \
    message.content_type in types.ContentTypes.AUDIO or \
    message.content_type in types.ContentTypes.TEXT: 
        text = message.html_text if message.html_text else message.md_text
    
    else:
        return

    message_id = message.message_id
    user_id = message.from_user.id
    chat_id = message.chat.id
    urls = await get_urls(text)

    if not urls:
        return 
    
    write_link_list = await db.select_all_write_links()
    urls = set(urls)
    if 'https://t.me' in urls:
        urls.remove('https://t.me')
    write_links = {item.get("link") for item in write_link_list if write_link_list}

    status = urls.issubset(write_links) 
    if status:
        return 

    black_user = await db.select_black_user(telegram_id=user_id)
    if not black_user:
        now_date = dt.now()
        await db.add_black_user(
            telegram_id=user_id,
            count=1,
            full_name=message.from_user.full_name,
            created_at=now_date
        )
        count = 1
    else:
        await db.update_black_user_count(telegram_id=user_id)
        count = black_user.get("count") + 1    

    if count >= MAX_ATTEMPT_FOR_BLOCK:
        await user_blocking(message)
        return
    
    service_message = await message.answer(text=f"Xurmatli {message.from_user.full_name}[<a href=\'tg://user?id={message.from_user.id}\'>{message.from_user.id}</a>] guruhga reklama yuborish mumkin emas.\nSiz {count}/{MAX_ATTEMPT_FOR_BLOCK} ogohlantirishga egasiz, ehtiyot bo'ling!")
    await bot.delete_message(chat_id, message_id)
    await asyncio.sleep(6)
    await bot.delete_message(chat_id, service_message.message_id)
