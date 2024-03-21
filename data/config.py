from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS")
IP = env.str("ip")

UNTIL_DATE = 1 # 2
MAX_ATTEMPT_FOR_BLOCK = 4
COUNT_FOR_READ_ONLY = 2 

DB_USER = env.str("DB_USER")
DB_PASS = env.str("DB_PASS")
DB_NAME = env.str("DB_NAME")
DB_HOST = env.str("DB_HOST")


def add_admin_id(telegram_id):
    ADMINS.append(telegram_id)