import logging
import os
import asyncpg

from aiogram import types
from datetime import datetime, UTC

logger = logging.getLogger(__name__)


async def connect(message: types.Message) -> None:
    """
    It connects to the Postgresql db and saves the user's id, name, lang.
    If there is not an environmental var `DATABASE_URL` (for example, if you run the bot locally),
    it will the url from the defaults
    """
    id = int(message["from"]["id"])
    lang = message.text.strip("👍").strip("🤝").strip()
    name = message["from"]["first_name"]
    last_seen = datetime.now(UTC)  # This is UTC+0
    # The date in the db will be timezone aware (UTC+2 for Greece)
    date_added = last_seen
    if not os.environ.get("DATABASE_URL"):
        # ``postgres://user:pass@host:port/database?option=value``
        host = "127.0.0.1"
        port = 5432
        user = "postgres"
        database = "postgres"
        password = os.environ.get("dbpass")
        os.environ["DATABASE_URL"] = f"postgres://{user}:{password}@{host}:{port}/{database}"
    async with asyncpg.create_pool(
        dsn=os.environ.get("DATABASE_URL"),
        # host="127.0.0.1", database="postgres", user="postgres", password=os.environ.get("dbpass")
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
                    lang TEXT NOT NULL,
                    date_added timestamp with time zone,
                    last_seen timestamp with time zone
                );
                """
            )

            await conn.execute(
                """
                ALTER TABLE users
                    ADD if not exists id BIGINT PRIMARY KEY,
                    ADD if not exists name TEXT NOT NULL,
                    ADD if not exists lang TEXT NOT NULL,
                    ADD if not exists date_added timestamp with time zone,
                    ADD if not exists last_seen timestamp with time zone;
                """
            )

            await conn.execute(
                """
               INSERT INTO users(id,name,lang,date_added,last_seen) VALUES($1,$2,$3,$4,$5)
               ON CONFLICT(id)
               DO UPDATE SET
                   name = $2,
                   lang = $3,
                   last_seen = $5,
                   date_added = (
                        CASE
                            WHEN users.date_added IS NULL THEN $4
                            ELSE (
                                SELECT users.date_added FROM users WHERE id=$1
                            )
                        END
                   );
                """,
                id,
                name,
                lang,
                date_added,
                last_seen,
            )

            logger.info(await conn.execute("""SELECT id,name,lang FROM users;"""))
            # https://magicstack.github.io/asyncpg/current/api/index.html#asyncpg.connection.Connection.fetch
            rows = await conn.fetch("""SELECT * FROM users;""")
            logger.info(rows)
