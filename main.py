"""Main module"""
import logging
import os
import colorama
from aiogram import Dispatcher
from aiogram.utils import executor

# from aiogram.enums import ParseMode https://github.com/aiogram/aiogram/blob/v3.0.0/examples/echo_bot.py
import config

from src.helper.helper import parse_arguments, color_logging
from src.scheduler.funcs import start_scheduler_as_task

# This is a hacky way to parse the variables and save the user's preference of DEBUG etc
if __name__ == "__main__":
    args = parse_arguments()
    DEBUG, MODE, TEST = args.debug, args.mode, args.test
    config.DEBUG, config.MODE, config.TEST = DEBUG, MODE, TEST
    os.environ["dbpass"] = args.dbpass

# These need to be here, otherwise the imports are messed up!
from src.bot.bot_functions import dp


def main(debug: bool, dp: Dispatcher) -> None:
    level = logging.DEBUG if debug else logging.INFO
    console = color_logging(level=level)
    logging.basicConfig(
        level=level,
        force=True,
        handlers=[console],
    )  # Force is needed here to re config logging
    colorama.init(convert=True)
    logging.info(f"DEBUG: {debug}, MODE: {MODE}, TEST: {TEST}")

    executor.start_polling(
        dispatcher=dp,
        timeout=60,
        on_startup=start_scheduler_as_task,
        skip_updates=True,
    )


if __name__ == "__main__":
    main(debug=config.DEBUG, dp=dp)
