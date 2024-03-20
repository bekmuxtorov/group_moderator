from aiogram.dispatcher.filters.state import State, StatesGroup


class AddAdmin(StatesGroup):
    admin_id = State()