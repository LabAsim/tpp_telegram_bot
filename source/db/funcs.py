import logging
import os


# conn = psycopg2.connect(
#     host="localhost",
#     database="postgres",
#     user="postgres",
#     password="Abcd1234")
# async def connect():
#     """ Connect to the PostgreSQL database server """
#     #conn = None
#     try:
#         # read connection parameters
#         #params = config()
#
#         # connect to the PostgreSQL server
#         print('Connecting to the PostgreSQL database...')
#         #conn = psycopg2.connect(**params)
#
#         # create a cursor
#         cur = conn.cursor()
#         #cur.execute("""PRAGMA encoding = 'UTF-8';""")
#         # execute a statement
#         print('PostgreSQL database version:')
#         await cur.execute('SELECT version()')
#
#         # display the PostgreSQL database server version
#         db_version = await cur.fetchone()
#         print(db_version)
#         cur.execute("""
#                         CREATE TABLE IF NOT EXISTS users(
#                             id INT PRIMARY KEY,
#                             name TEXT NOT NULL,
#                             lang TEXT NOT NULL);
#                         """)
#         conn.commit()
#         # cur.execute(f"""
#         #                                INSERT INTO news users(?,?)
#         #                                ON CONFLICT(news.id) DO UPDATE SET
#         #                                    name = ?,
#         #                                    lang = ?;
#         #                                """, list_to_insert)
#         # close the communication with the PostgreSQL
#         cur.close()
#     except (Exception, psycopg2.DatabaseError) as error:
#         print(error)
#     finally:
#         if conn is not None:
#             conn.close()
#             print('Database connection closed.')


# if __name__ == '__main__':
#     connect()

import asyncpg
from aiogram import types


async def connect(message: types.Message) -> None:
    id = int(message["from"]["id"])
    lang = message.text.strip("👍").strip("🤝").strip()
    name = message["from"]["first_name"]
    conn = await asyncpg.connect(
        host="127.0.0.1", database="postgres", user="postgres", password=os.environ.get("dbpass")
    )
    # ψur = conn.cursor()
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users(
            id INT PRIMARY KEY,
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
    logging.debug(await conn.execute("""SELECT * FROM users"""))
    await conn.close()
