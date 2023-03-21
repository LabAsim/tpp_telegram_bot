import time

import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton  # for reply keyboard (sends message)
from saved_tokens import token_apify, token_telegram_bot, token_telegram_bot_test
import logging
from source.bot.bot import BotConstructor


def app(event):
    #
    bot = BotConstructor(telegram_token=token_telegram_bot_test, apify_token=token_apify)
    logging.basicConfig(level=logging.DEBUG)
    # this is the last line
    executor.start_polling(bot.dp, timeout=20)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app(event=None)
