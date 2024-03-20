from data.config import add_admin_id

async def add_admin(db):
    data = await db.select_all_admin()
    if data:
        [add_admin_id(item.get("telegram_id")) for item in data]
