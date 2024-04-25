from aiogram import Dispatcher

from loader import dp
from .throttling import ThrottlingMiddleware, AlbumMiddleware


if __name__ == "middlewares":
    dp.middleware.setup(AlbumMiddleware())
    dp.middleware.setup(ThrottlingMiddleware())
