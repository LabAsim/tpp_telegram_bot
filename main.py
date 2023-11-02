"""Main module"""
import logging
import os

import colorama
from aiogram import Dispatcher
from aiogram.utils import executor

# from aiogram.enums import ParseMode https://github.com/aiogram/aiogram/blob/v3.0.0/examples/echo_bot.py
import config
from source.helper.helper import parse_arguments, color_logging

# This is a hacky way to parse the variables and save the user's preference of DEBUG etc
if __name__ == "__main__":
    args = parse_arguments()
    DEBUG, MODE, TEST = args.debug, args.mode, args.test
    config.DEBUG, config.MODE, config.TEST = DEBUG, MODE, TEST
    os.environ["dbpass"] = args.dbpass

from source.bot.bot_functions import dp

colorama.init(convert=True)


def main(debug: bool, dp: Dispatcher):
    if debug:
        console = color_logging(level=logging.DEBUG)
        logging.basicConfig(
            level=logging.DEBUG,
            force=True,
            handlers=[console],
        )  # Force is needed here to re config logging
        # color_logging(level=logging.DEBUG)
    else:
        # logging.basicConfig(level=logging.INFO, force=True)
        color_logging(level=logging.INFO)
    logging.info(f"DEBUG: {debug}, MODE: {MODE}, TEST: {TEST}")
    executor.start_polling(dp, timeout=60)


if __name__ == "__main__":
    # asyncio.run(main(debug=True, dp=dp))
    main(debug=config.DEBUG, dp=dp)
