from aiogram import Dispatcher

from loader import dp
from .group_chat import IsGroup
from .private_chat import IsPrivate
from .is_admin import IsAdmin, IsBotAdmin


if __name__ == "filters":
    dp.filters_factory.bind(IsGroup)
    dp.filters_factory.bind(IsPrivate)
    dp.filters_factory.bind(IsAdmin)
    dp.filters_factory.bind(IsBotAdmin)

