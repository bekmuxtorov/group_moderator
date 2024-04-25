import re
import pytz
import asyncio
from datetime import datetime, timedelta
from aiogram import types, utils

from data.config import LOGS_CHANNEL


REGEXS = [
    r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+|www\.\S+',
    r'@\w+', r'https?:\/\/t\.me\/\+?[\w-]+',
    r'https?:\/\/www\.instagram\.com\/[\w-]+',
    r'https?:\/\/www\.facebook\.com\/[\w-]+',
    r'https?:\/\/youtube\.com\/@[\w-]+',
    r'https?:\/\/ummalife\.com\/[\w-]+',
]


async def get_urls(text: str):
    urls = []
    for regex in REGEXS:
        urls += re.findall(regex, text)
    return urls


async def delete_some_link(urls):
    if 'https://t.me' in urls:
        urls.remove('https://t.me')
    if 'https://www.instagram.com' in urls:
        urls.remove('https://www.instagram.com')
    if 'https://www.facebook.com' in urls:
        urls.remove('https://www.facebook.com')
    if 'https://youtube.com' in urls:
        urls.remove('https://youtube.com')
    if 'https://ummalife.com' in urls:
        urls.remove('https://ummalife.com')
    return urls


async def send_message_to_logs_channel(user_id, help_text):
    from loader import bot
    await bot.send_message(chat_id=LOGS_CHANNEL, text=f"\nUser_id: {user_id}\nAdd inform: {help_text}")


async def get_current_time():
    time_zone = pytz.timezone("Asia/Tashkent")
    return datetime.now(tz=time_zone)


async def user_read_only(message: types.Message, until_date: int, help_message: str, is_media_group: bool = False, album=None):
    member_id = message.from_user.id
    now_time = await get_current_time()
    until_date = now_time + timedelta(minutes=until_date)
    try:
        if is_media_group:
            for obj in album:
                await obj.delete()
        else:
            await message.delete()
        await message.chat.restrict(user_id=member_id, can_send_messages=False, until_date=until_date)
        await send_message_to_logs_channel(user_id=member_id, help_text=f"ℹ️ Hozirgi vaqt: {now_time.strftime('%Y-%m-%d %H:%M:%S %Z')}\n{until_date.strftime('%Y-%m-%d %H:%M:%S %Z')} gacha ro ga o'tkazildi.")
        service_message = await message.answer(text=help_message)
        await asyncio.sleep(12)
        await service_message.delete()

    except utils.exceptions.BadRequest as err:
        await send_message_to_logs_channel(user_id=member_id, help_text=f"❌ ro ga o'tkazish jarayonida, Xatolik! {err.args}")
        return


async def user_blocking(message: types.Message):
    user_id = message.from_user.id
    await message.chat.kick(user_id=user_id)
    await send_message_to_logs_channel(user_id=user_id, help_text="ℹ️ ban berildi")
    await message.delete()
    service_message = await message.answer(f"ℹ️ Foydalanuvchi {message.from_user.full_name}[<a href=\'tg://user?id={message.from_user.id}\'>{message.from_user.id}</a>] guruhdan haydaldi.")
    await asyncio.sleep(12)
    await service_message.delete()
