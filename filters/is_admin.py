from aiogram.dispatcher.filters import BoundFilter
from aiogram import types



class IsAdmin(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        member = await message.chat.get_member(message.from_user.id)
        return member.is_chat_admin()


class IsBotAdmin(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        from data.config import ADMINS
        return message.from_user.id in [int(item) for item in ADMINS]
        