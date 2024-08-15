"""Main module"""
import asyncio
import logging
import os
import colorama

from src.db.funcs import create_db_tables_startup

if __name__ == "__main__":
    # Set a different level for imported modules
    # See: https://stackoverflow.com/a/51529172
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("pytube").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("apify_client").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.INFO)

from aiogram import Dispatcher

# from aiogram.enums import ParseMode https://github.com/aiogram/aiogram/blob/v3.0.0/examples/echo_bot.py
import config

from src.helper.helper import parse_arguments, color_logging
from src.scheduler.funcs import start_scheduler_as_task

# This is a hacky way to parse the variables and save the user's preference of DEBUG etc
if __name__ == "__main__":
    args = parse_arguments()
    DEBUG, TEST = args.debug, args.test
    config.DEBUG, config.TEST = DEBUG, TEST
    os.environ["dbpass"] = args.dbpass

# These need to be here, otherwise the imports are messed up!
from src.bot.bot_functions import dp, bot
from src.bot.middleware import UserUpdateMiddleware


async def main(debug: bool, dp: Dispatcher) -> None:
    level = logging.DEBUG if debug else logging.INFO
    console = color_logging(level=level)
    logging.basicConfig(
        level=level,
        force=True,
        handlers=[console],
    )  # Force is needed here to re config logging
    # Init should be here so as the colors be rendered properly in fly.io
    colorama.init(convert=True)
    logging.info(f"DEBUG: {debug}, TEST: {TEST}")
    # Middleware needs to be registered here, otherwise it won't work!
    dp.message.outer_middleware(UserUpdateMiddleware())
    await start_scheduler_as_task()
    await create_db_tables_startup(pool=None)
    await dp.start_polling(
        bot,
        timeout=20,
        skip_updates=False,
    )


if __name__ == "__main__":
    asyncio.run(main(debug=config.DEBUG, dp=dp))
