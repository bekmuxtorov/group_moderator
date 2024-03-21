import re
import datetime
import asyncio
from datetime import datetime as dt

from aiogram.dispatcher.filters import Command
from aiogram import types
from aiogram.utils.exceptions import BadRequest

from filters.is_admin import IsAdmin
from loader import dp, db, bot
from filters import IsGroup
from data.config import MAX_ATTEMPT_FOR_BLOCK, COUNT_FOR_READ_ONLY, UNTIL_DATE, ADMINS
from utils.moderator_utils import get_urls
 

async def user_read_only(message:types.Message):
    member_id = message.from_user.id
    until_date = datetime.datetime.now() + datetime.timedelta(minutes=UNTIL_DATE)
    try:
        await message.chat.restrict(user_id=member_id, can_send_messages=False, until_date=until_date)
        service_message = await message.answer(text=f"Xurmatli {message.from_user.full_name}[<a href=\'tg://user?id={message.from_user.id}\'>{message.from_user.id}</a>] guruhga reklama yuborish mumkin emas.\nSiz {COUNT_FOR_READ_ONLY}/{COUNT_FOR_READ_ONLY} ogohlantirishga egasiz va {UNTIL_DATE} daqiqa guruhga yoza olmaysiz, keyingi safar guruhdan haydalasiz. Extiyot bo'ling!")
        await message.delete()
        await asyncio.sleep(6)
        await service_message.delete()

    except BadRequest as err:
        await message.answer(f"Xatolik! {err.args}")
        return

async def user_blocking(message: types.Message):
    user_id = message.from_user.id
    await message.chat.kick(user_id=user_id)
    await message.delete()
    service_message = await message.answer(f"Foydalanuvchi {message.from_user.full_name}[<a href=\'tg://user?id={message.from_user.id}\'>{message.from_user.id}</a>] guruhdan haydaldi.")
    await asyncio.sleep(5)
    await service_message.delete()



# /ro oki !ro (read-only) komandalari uchun handler
# foydalanuvchini read-only ya'ni faqat o'qish rejimiga o'tkazib qo'yamiz.
@dp.message_handler(IsGroup(), Command("ro", prefixes="!/"), IsAdmin())
async def read_only_mode(message: types.Message):
    member = message.reply_to_message.from_user
    member_id = member.id
    command_parse = re.compile(r"(!ro|/ro) ?(\d+)? ?([\w+\D]+)?")
    parsed = command_parse.match(message.text)
    time = parsed.group(2)
    comment = parsed.group(3)
    if not time:
        time = 5

    """
    !ro 
    !ro 5 
    !ro 5 test
    !ro test
    !ro test test test
    /ro 
    /ro 5 
    /ro 5 test
    /ro test
    """
    # 5-minutga izohsiz cheklash
    # !ro 5
    # command='!ro' time='5' comment=[]

    # 50 minutga izoh bilan cheklash
    # !ro 50 reklama uchun ban
    # command='!ro' time='50' comment=['reklama', 'uchun', 'ban']

    time = int(time)

    # Ban vaqtini hisoblaymiz (hozirgi vaqt + n minut)
    until_date = datetime.datetime.now() + datetime.timedelta(minutes=time)

    try:
        await message.chat.restrict(user_id=member_id, can_send_messages=False, until_date=until_date)
        await message.reply_to_message.delete()
    except BadRequest as err:
        await message.answer(f"Xatolik! {err.args}")
        return

    service_message = await message.answer(f"Xurmatli {message.reply_to_message.from_user.full_name}[<a href=\'tg://user?id={message.reply_to_message.from_user.id}\'>{message.reply_to_message.from_user.id}</a>] {time} daqiqa yozish huquqidan mahrum qilindingiz.\n"
                         f"Sabab: \n<b>{comment}</b>")

    await asyncio.sleep(5)
    await message.delete()
    await service_message.delete()


@dp.message_handler(IsGroup(), content_types=types.ContentTypes.NEW_CHAT_MEMBERS)
async def ban(message: types.Message):
    await message.delete()
    text = f"""Assalomu alaykum {message.from_user.full_name}[<a href=\'tg://user?id={message.from_user.id}\'>{message.from_user.id}</a>].\n<b>Himmat 700+</b> loyihasining muhokama guruhiga xush kelibsiz!"""
    service_message = await message.answer(text)
    await asyncio.sleep(6)
    await service_message.delete()

@dp.message_handler(IsGroup(), content_types=types.ContentTypes.LEFT_CHAT_MEMBER)
async def ban(message: types.Message):
    await message.delete()


@dp.message_handler(IsGroup(), Command("unban", prefixes="!/"), IsAdmin())
async def unban(message: types.Message):
    command_parse = re.match(r'^\/unban\s+(\d+)$', message.text)
    if not command_parse:
        return     

    member_id = int((message.text).split(' ')[1])
    block_user = await db.select_black_user(telegram_id=member_id)
    if not block_user:
        service_message = await  message.answer("⚡Bu user ban olmagan!")
        await message.delete()
        await asyncio.sleep(5)
        await service_message.delete()
        return 

    await message.chat.unban(user_id=member_id, only_if_banned=True)
    await db.delete_black_user(telegram_id=member_id)
    service_message = await message.answer(f"Foydalanuvchi {block_user.get('full_name')} bandan chiqarildi!")
    await message.delete()
    await asyncio.sleep(6)
    await service_message.delete()


@dp.message_handler(IsGroup(), content_types=types.ContentTypes.ANY)
async def ban(message: types.Message):
    member = await message.chat.get_member(message.from_user.id)
    if member.is_chat_admin(): return 

    if message.from_user.id in [int(item) for item in ADMINS]: return
    
    if (message.content_type in types.ContentTypes.PHOTO or \
    message.content_type in types.ContentTypes.VIDEO or \
    message.content_type in types.ContentTypes.AUDIO or \
    message.content_type in types.ContentTypes.TEXT) and (message.html_text or message.md_text): 
        text = message.html_text if message.html_text else message.md_text
    
    else:
        return

    user_id = message.from_user.id
    urls = await get_urls(text)

    if not urls:
        return 
    
    write_link_list = await db.select_all_write_links()
    urls = set(urls)
    if 'https://t.me' in urls: urls.remove('https://t.me')
    if 'https://www.instagram.com' in urls: urls.remove('https://www.instagram.com')
    if 'https://www.facebook.com' in urls: urls.remove('https://www.facebook.com')
    if 'https://youtube.com' in urls: urls.remove('https://youtube.com')
    if 'https://ummalife.com' in urls: urls.remove('https://ummalife.com')
    
    write_links = {item.get("link") for item in write_link_list if write_link_list}
    print('='*9)
    print(f'write_link_list: {write_links}')
    print(f'urls: {urls}')
    print('='*9)

    status = urls.intersection(write_links)
    print(status)
    print(bool(status))
    # status = urls.issubset(write_links) 
    if status:
        return 

    print("add block ga yaqin")
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

    if count == COUNT_FOR_READ_ONLY:
        await user_read_only(message)
        return 

    if count >= MAX_ATTEMPT_FOR_BLOCK:
        await user_blocking(message)
        return
    
    print("add block ga oldida")
    await message.delete()
    if count + 1 == MAX_ATTEMPT_FOR_BLOCK:
        service_message = await message.answer(text=f"Xurmatli {message.from_user.full_name}[<a href=\'tg://user?id={message.from_user.id}\'>{message.from_user.id}</a>] guruhga reklama yuborish mumkin emas.\nSiz {count}/{MAX_ATTEMPT_FOR_BLOCK} ogohlantirishga egasiz.\n\nKeyingi safar guruhdan hayalasiz. Ehtiyot bo'ling!")
    else: 
        service_message = await message.answer(text=f"Xurmatli {message.from_user.full_name}[<a href=\'tg://user?id={message.from_user.id}\'>{message.from_user.id}</a>] guruhga reklama yuborish mumkin emas.\nSiz {count}/{MAX_ATTEMPT_FOR_BLOCK} ogohlantirishga egasiz, ehtiyot bo'ling!")
    await asyncio.sleep(6)
    await service_message.delete()
