import logging
import os
import asyncpg

from aiogram import types


async def connect(message: types.Message) -> None:
    """
    It connects to the Postgresql db and saves the user's id, name, lang.
    If there is not an environmental var `DATABASE_URL` (for example, if you run the bot locally),
    it will the url from the defaults
    """
    id = int(message["from"]["id"])
    lang = message.text.strip("👍").strip("🤝").strip()
    name = message["from"]["first_name"]
    if not os.environ.get("DATABASE_URL"):
        # ``postgres://user:pass@host:port/database?option=value``
        host = "127.0.0.1"
        port = 5432
        user = "postgres"
        database = "postgres"
        password = os.environ.get("dbpass")
        os.environ["DATABASE_URL"] = f"postgres://{user}:{password}@{host}:{port}/{database}"
    async with asyncpg.create_pool(
        dsn=os.environ.get("DATABASE_URL")
        # host="127.0.0.1", database="postgres", user="postgres", password=os.environ.get("dbpass")
        ,
        command_timeout=60,
    ) as pool:
        async with pool.acquire() as conn:
            # async with asyncpg.connect(
            #     host="127.0.0.1", database="postgres", user="postgres", password=os.environ.get("dbpass")
            # ) as conn:
            # ψur = conn.cursor()
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users(
                    id BIGINT PRIMARY KEY,
                    name TEXT NOT NULL,
                    lang TEXT NOT NULL
                );
                """
            )
            # await conn.commit()

            await conn.execute(
                """
               INSERT INTO users(id,name,lang) VALUES($1,$2,$3)
               ON CONFLICT(id)
               DO UPDATE SET
                   name = $2,
                   lang = $3;
                """,
                id,
                name,
                lang,
            )
            logging.debug(await conn.execute("""SELECT id,name,lang FROM users;"""))
            # https://magicstack.github.io/asyncpg/current/api/index.html#asyncpg.connection.Connection.fetch
            rows = await conn.fetch("""SELECT id,name,lang FROM users;""")
            logging.debug(rows)
