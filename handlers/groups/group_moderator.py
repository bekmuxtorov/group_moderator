import pytz
import re
import asyncio
from datetime import datetime

from aiogram.dispatcher.filters import Command
from aiogram import types
from aiogram.utils.exceptions import BadRequest

from filters.is_admin import IsAdmin
from loader import dp, db, bot
from filters import IsGroup
from data.config import ADMINS, FIRST_RO_TIME, SECOND_RO_TIME
from utils.moderator_utils import get_urls, delete_some_link, send_message_to_logs_channel, user_read_only, user_blocking


@dp.message_handler(IsGroup(), content_types=types.ContentTypes.NEW_CHAT_MEMBERS)
async def new_user_greeting(message: types.Message):
    text = f"""Assalomu alaykum {message.from_user.full_name}[<a href=\'tg://user?id={message.from_user.id}\'>{message.from_user.id}</a>].\n<b>Himmat 700+</b> loyihasining muhokama guruhiga xush kelibsiz!"""
    service_message = await message.answer(text)
    all_info_of_chat = message.chat
    await message.delete()
    await send_message_to_logs_channel(user_id=message.from_user.id, help_text=f"ℹ️ guruhga yangi a'zo qo'shildi va xabar o'chirildi. \n\n{all_info_of_chat}")
    await asyncio.sleep(12)
    await service_message.delete()


@dp.message_handler(IsGroup(), content_types=types.ContentTypes.LEFT_CHAT_MEMBER)
async def left_user(message: types.Message):
    all_info_of_chat = message.chat
    await message.delete()
    await send_message_to_logs_channel(user_id=message.from_user.id, help_text=f"ℹ️ guruhdan tark etdi va xabar o'chirildi. \n\n{all_info_of_chat}")


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

    time = int(time)
    await user_read_only(
        message=message,
        until_date=time,
        help_message=comment,
        member_id=member_id
    )

    service_message = await message.answer(f"Xurmatli {message.reply_to_message.from_user.full_name}[<a href=\'tg://user?id={message.reply_to_message.from_user.id}\'>{message.reply_to_message.from_user.id}</a>] {time} daqiqa yozish huquqidan mahrum qilindingiz.\n"
                                           f"Sabab: \n<b>{comment}</b>")
    await asyncio.sleep(5)
    await message.delete()
    await service_message.delete()


@dp.message_handler(IsGroup(), Command("unban", prefixes="!/"), IsAdmin())
async def unban(message: types.Message):
    command_parse = re.match(r'^\/unban\s+(\d+)$', message.text)
    if not command_parse:
        await send_message_to_logs_channel(user_id=message.from_user.id, help_text="❌ /unban buyrug'ini berishda xatolik")
        return

    all_info_of_chat = message.chat
    member_id = int((message.text).split(' ')[1])
    block_user = await db.select_black_user(telegram_id=member_id)
    chat_member = await bot.get_chat_member(chat_id=message.chat.id, user_id=member_id)
    if chat_member.status == "kicked":
        await bot.unban_chat_member(chat_id=message.chat.id, user_id=member_id)
        await db.delete_black_user(telegram_id=member_id)
        service_message = await message.answer(f"Foydalanuvchi {block_user.get('full_name')}[{block_user.get('telegram_id')}] bandan chiqarildi!")
        await message.delete()
        await send_message_to_logs_channel(user_id=member_id, help_text=f"ℹ️ User bandan chiqarildi \n\nchat_info: {all_info_of_chat}")

        await asyncio.sleep(12)
        await service_message.delete()
    else:
        chat_name = message.chat.full_name
        service_message = await message.answer(f"⚡Foydalanuvchi <b>{chat_name}</b> guruhida ban olmagan!")
        await send_message_to_logs_channel(user_id=member_id, help_text=f"ℹ️ user bu guruhdan ban olmagan! \n\nchat_info: {all_info_of_chat}")
        await message.delete()
        await asyncio.sleep(12)
        await service_message.delete()


@dp.message_handler(IsGroup(), content_types=types.ContentTypes.TEXT)
@dp.message_handler(IsGroup(), content_types=types.ContentTypes.AUDIO)
@dp.message_handler(IsGroup(), content_types=types.ContentTypes.VIDEO)
@dp.message_handler(IsGroup(), content_types=types.ContentTypes.PHOTO)
@dp.message_handler(IsGroup(), content_types=types.ContentTypes.DOCUMENT)
async def ban(message: types.Message):
    member = await message.chat.get_member(message.from_user.id)
    if member.is_chat_admin():
        return

    if message.from_user.id in [int(item) for item in ADMINS]:
        return

    text = message.html_text if message.html_text else message.md_text
    urls = await get_urls(text)

    if not urls:
        return
    urls = await delete_some_link(set(urls))

    user_id = message.from_user.id
    all_info_of_chat = message.chat
    await send_message_to_logs_channel(user_id=user_id, help_text=f"ℹ️ xabarda linklar aniqlandi\n\n{urls} \n\n{all_info_of_chat}")

    write_link_list = await db.select_all_write_links()

    write_links = {item.get("link")
                   for item in write_link_list if write_link_list}

    status = urls.intersection(write_links)
    if status:
        return

    black_user = await db.select_black_user(telegram_id=user_id)
    if not black_user:
        group_id = message.chat.id
        group_name = message.chat.full_name
        now_date = pytz.timezone('Asia/Tashkent').localize(datetime.now())
        await db.add_black_user(
            telegram_id=user_id,
            count=1,
            full_name=message.from_user.full_name,
            created_at=now_date,
            group_id=group_id,
            group_name=group_name,
            ban_status=False
        )
        count = 1
        await send_message_to_logs_channel(user_id=user_id, help_text=f"ℹ️ birinchi marta reklama jo'natildi va bazaga qo'shildi \n\n{all_info_of_chat}")

    else:
        await db.update_black_user_count(telegram_id=user_id)
        count = black_user.get("count") + 1

    # Userning reklama jo'natgan xabarlarining soniga ko'ra, unga xukm beriladi!
    await send_message_to_logs_channel(user_id=user_id, help_text=f"ℹ️ {user_id}: {count}ta")
    if count == 1:
        help_message = f"Xurmatli {message.from_user.full_name}[<a href=\'tg://user?id={message.from_user.id}\'>{message.from_user.id}</a>] guruhga reklama yuborish mumkin emas.\nSiz 1/3 ogohlantirishga egasiz va {FIRST_RO_TIME} daqiqa guruhga yoza olmaysiz.\n\nKeyingi safar 3 kun guruhga yoza olmaysiz. Ehtiyot bo'ling!"
        await user_read_only(message=message, until_date=FIRST_RO_TIME, help_message=help_message, member_id=user_id)
        return

    elif count == 2:
        help_message = f"Xurmatli {message.from_user.full_name}[<a href=\'tg://user?id={message.from_user.id}\'>{message.from_user.id}</a>] guruhga reklama yuborish mumkin emas.\nSiz 2/3 ogohlantirishga egasiz va {SECOND_RO_TIME / (24 * 60)} kun guruhga yoza olmaysiz.\n\nKeyingi safar guruhdan haydalasiz. Ehtiyot bo'ling!"
        await user_read_only(message=message, until_date=SECOND_RO_TIME, help_message=help_message, member_id=user_id)
        return

    else:
        await user_blocking(message)
        return
