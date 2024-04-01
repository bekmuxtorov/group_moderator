from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS")
IP = env.str("ip")

LOGS_CHANNEL = env.str("LOGS_CHANNEL")

FIRST_RO_TIME = 5
SECOND_RO_TIME = 3 * 24 * 60
LAST_RO_TIME = 7 * 24 * 60

DB_USER = env.str("DB_USER")
DB_PASS = env.str("DB_PASS")
DB_NAME = env.str("DB_NAME")
DB_HOST = env.str("DB_HOST")


def add_admin_id(telegram_id):
    ADMINS.append(telegram_id)
