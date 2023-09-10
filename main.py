"""Main module"""
import asyncio
import logging
from aiogram import Dispatcher
from aiogram.utils import executor
# from aiogram.enums import ParseMode https://github.com/aiogram/aiogram/blob/v3.0.0/examples/echo_bot.py
import config
from source.helper.helper import parse_arguments

# This is a hacky way to parse the variables and save the user's preference of DEBUG etc
if __name__ == '__main__':
    args = parse_arguments()
    DEBUG, MODE = args.debug, args.mode
    config.DEBUG, config.MODE = True, MODE

from source.bot.bot_functions import dp


def main(debug: bool, dp: Dispatcher):
    if debug:
        logging.basicConfig(level=logging.DEBUG, force=True)  # Force is needed here to re config logging
    else:
        logging.basicConfig(level=logging.INFO, force=True)
    executor.start_polling(dp, timeout=25)


if __name__ == '__main__':
    # asyncio.run(main(debug=True, dp=dp))
    main(debug=True, dp=dp)
