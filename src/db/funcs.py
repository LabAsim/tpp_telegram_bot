import logging
import os
from typing import Optional

import asyncpg
import datetime

from aiogram import types

logger = logging.getLogger(__name__)


class DbPoolSingleton:
    """
    A class to manage the pool for the db.
    See: https://stackoverflow.com/a/76586245
    Alternative use: `async with asyncpg.create_pool(dsn=database_url,) as pool:`
    """

    db_pool: Optional[asyncpg.pool.Pool] = None

    @staticmethod
    async def create_pool():
        database_url = construct_database_url()
        pool: asyncpg.Pool = await asyncpg.create_pool(dsn=database_url, min_size=1, max_size=6)
        logger.info("Database Pool created")
        return pool

    @staticmethod
    async def get_pool() -> asyncpg.pool.Pool:
        if not DbPoolSingleton.db_pool:
            DbPoolSingleton.db_pool = await DbPoolSingleton.create_pool()
        logger.debug("Fetching pool")
        return DbPoolSingleton.db_pool

    @staticmethod
    async def terminate_pool():
        (await DbPoolSingleton.get_pool()).terminate()
        DbPoolSingleton.db_pool = None
        logger.warning("Database Pool terminated")


def construct_database_url() -> str:
    """If there is not an environmental variable, it creates a new one based on defaults"""
    if not os.environ.get("DATABASE_URL"):
        # ``postgres://user:pass@host:port/database?option=value``
        host = "127.0.0.1"
        port = 5432
        user = "postgres"
        database = os.environ.get("database", "postgres")
        password = os.environ.get("dbpass")
        os.environ["DATABASE_URL"] = f"postgres://{user}:{password}@{host}:{port}/{database}"

    return os.environ["DATABASE_URL"]


async def connect(message: types.Message) -> None:
    """
    It connects to the Postgresql db and saves the user's id, name, lang.
    If there is not an environmental var `DATABASE_URL` (for example, if you run the bot locally),
    it will use the url from the defaults
    """
    id = int(message.from_user.id)
    lang = message.text.strip("👍").strip("🤝").strip()
    name = message.from_user.first_name
    last_seen = datetime.datetime.now(datetime.timezone.utc)  # This is UTC+0
    # The date in the db will be timezone aware (UTC+2 for Greece)
    date_added = last_seen
    pool = await DbPoolSingleton.get_pool()
    async with pool.acquire() as conn:
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


async def update_user_info(message: types.Message) -> None:
    """Updates the user's info"""
    if not message:
        # If there is no messages at all
        return None
    print(message.from_user.id)
    id = int(message.from_user.id)
    lang = "English"
    name = message.from_user.first_name
    last_seen = datetime.datetime.now(datetime.timezone.utc)  # This is UTC+0
    # The date in the db will be timezone aware (UTC+2 for Greece)
    pool = await DbPoolSingleton.get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
           INSERT INTO users(id,name,lang,last_seen,date_added) VALUES($1,$2,$3,$4,$4)
           ON CONFLICT(id)
           DO UPDATE SET
               name = $2,
               lang = (
                    CASE
                        WHEN users.lang IS NULL THEN $3
                        ELSE (
                            SELECT users.lang FROM users WHERE id=$1
                        )
                    END
               ),
               last_seen = $4,
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
            last_seen,
        )

        # logger.info(await conn.execute("""SELECT id,name,lang FROM users;"""))
        # https://magicstack.github.io/asyncpg/current/api/index.html#asyncpg.connection.Connection.fetch
        rows = await conn.fetch("""SELECT * FROM users;""")
        logger.debug(rows)


async def fetch_lang(message: types.Message) -> asyncpg.Record:
    """Returns the language preference of the user"""
    id = int(message.from_user.id)
    database_url = construct_database_url()
    conn = await asyncpg.connect(dsn=database_url)
    # https://magicstack.github.io/asyncpg/current/api/index.html#asyncpg.connection.Connection.fetch
    rows = await conn.fetch("""SELECT lang FROM users WHERE users.id = $1;""", id)

    logger.debug(rows)

    return rows[0]


async def fetch_schedule(message: types.Message) -> list[asyncpg.Record]:
    """Fetches the schedule of the user (based on `id.`)"""
    chat_id = str(message.from_user.id)
    chat_id_with_dot = chat_id + "."  # This distinguishes the user id from schedule id
    database_url = construct_database_url()
    conn = await asyncpg.connect(dsn=database_url)
    rows = await conn.fetch(
        """SELECT * FROM schedules WHERE schedules.id LIKE  $1 || '%' ;""", chat_id_with_dot
    )
    logger.debug(rows)
    return rows


async def delete_target_schedule(target_id: str) -> None:
    """Deletes the target schedule"""
    database_url = construct_database_url()
    conn = await asyncpg.connect(dsn=database_url)
    await conn.execute("""delete from schedules where id = $1""", target_id)
