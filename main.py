"""Main module"""
import logging
from aiogram import executor
from config import DEBUG
# Import all the bot methods
from source.bot.bot_functions import dp
from source.helper.helper import parse_arguments


def app(event, debug=False):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    executor.start_polling(dp, timeout=20)


if __name__ == '__main__':
    app(event=None, debug=DEBUG)
