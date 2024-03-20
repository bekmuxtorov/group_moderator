from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config

class Database:

    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    async def create_write_link_list(self):
        sql = """
        CREATE TABLE IF NOT EXISTS write_link_list(
            id SERIAL PRIMARY KEY,
            link VARCHAR(255) NOT NULL,
            added_by VARCHAR(255) NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW() 
        )
        """
        await self.execute(sql, execute=True)

    async def create_black_user_list(self):
        sql = """
        CREATE TABLE IF NOT EXISTS black_user_list(
            telegram_id BIGINT NOT NULL UNIQUE,
            full_name VARCHAR(255) NOT NULL,
            count integer NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW() 
        )
        """
        await self.execute(sql, execute=True)

    async def create_admins(self):
        sql = """
        CREATE TABLE IF NOT EXISTS admins(
            telegram_id BIGINT NOT NULL UNIQUE,
            full_name VARCHAR(255) NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW() 
        )
        """
        await self.execute(sql, execute=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    async def add_admin(self, telegram_id, full_name, created_at):
        sql = "INSERT INTO admins (telegram_id, full_name, created_at) VALUES($1, $2, $3) returning *"
        return await self.execute(sql, telegram_id, full_name, created_at, fetchrow=True)
        
    async def select_all_admin(self):
        sql = "SELECT * FROM admins"
        data = await self.execute(sql, fetch=True)
        return [
            {
                "telegram_id": item[0],
                "full_name": item[1],
                "created_at": item[2]
            } for item in data
        ] if data else []

    async def add_write_link_list(self, link, added_by, created_at):
        sql = "INSERT INTO write_link_list (link, added_by, created_at) VALUES($1, $2, $3) returning *"
        return await self.execute(sql, link, added_by, created_at, fetchrow=True)

    async def select_all_write_links(self):
        sql = "SELECT * FROM write_link_list"
        data = await self.execute(sql, fetch=True)
        return [
            {
                "id": item[0],
                "link": item[1],
                "added_by": item[2],
                "created_at": item[3]
            } for item in data
        ] if data else []

    async def select_write_link(self, **kwargs):
        sql = "SELECT * FROM write_link_list WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        data = await self.execute(sql, *parameters, fetchrow=True)
        return {
            "id": data[0],
            "link": data[1],
            "added_by": data[2],
            "created_at": data[3]
        } if data else None

    async def delete_write_link(self, link_id):
        await self.execute("DELETE FROM write_link_list WHERE id=$1", link_id, execute=True)

    async def add_black_user(self, telegram_id, count, full_name, created_at):
        sql = "INSERT INTO black_user_list (telegram_id, count, full_name, created_at) VALUES($1, $2, $3, $4) returning *"
        return await self.execute(sql, telegram_id, count, full_name, created_at, fetchrow=True)
        
    async def select_all_black_user_list(self):
        sql = "SELECT * FROM black_user_list"
        data = await self.execute(sql, fetch=True)
        return [
            {
                "telegram_id": item[0],
                "full_name": item[1],
                "count": item[2],
                "created_at": item[3]
            } for item in data
        ] if data else []

    async def update_black_user_count(self, telegram_id):
        sql = "UPDATE black_user_list SET count = count+1 WHERE telegram_id=$1;"
        return await self.execute(sql, telegram_id, execute=True)

    async def select_black_user(self, **kwargs):
        sql = "SELECT * FROM black_user_list WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        data = await self.execute(sql, *parameters, fetchrow=True)
        return {
            "telegram_id": data[0],
            "full_name": data[1],
            "count": data[2],
            "created_at": data[3]
        } if data else None

    async def delete_black_user(self, telegram_id):
        await self.execute("DELETE FROM black_user_list WHERE telegram_id=$1", telegram_id, execute=True)

    async def select_all_users(self):
        sql = "SELECT * FROM Users"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM Users"
        return await self.execute(sql, fetchval=True)

    async def update_user_username(self, username, telegram_id):
        sql = "UPDATE Users SET username=$1 WHERE telegram_id=$2"
        return await self.execute(sql, username, telegram_id, execute=True)

    async def delete_users(self):
        await self.execute("DELETE FROM Users WHERE TRUE", execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE Users", execute=True)
