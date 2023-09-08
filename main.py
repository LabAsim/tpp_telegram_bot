"""Main module"""
import logging
from aiogram import executor, Dispatcher
from config import PROXY_URL_PYTHONANYWHERE
from saved_tokens import TOKEN_APIFY
from source.bot.bot_dispatcher import botify, choose_token
from source.bot.bot_functions import register_functions
# Import all the bot methods
from source.bot.botvalues import BotConstructor
from source.helper.helper import parse_arguments


def main(debug: bool, mode: str) -> None:
    token = choose_token(debug=debug)
    bot = botify(token=token, proxy_url=PROXY_URL_PYTHONANYWHERE, mode=mode)
    dp = Dispatcher(bot)
    _bot = BotConstructor(telegram_token=choose_token(), apify_token=TOKEN_APIFY, dispatcher=dp, debug=debug)
    register_functions(dp=dp, _bot=_bot)

    if debug:
        logging.basicConfig(level=logging.DEBUG)
    executor.start_polling(dp, timeout=25)


if __name__ == '__main__':
    args = parse_arguments()
    DEBUG, MODE = args.debug, args.mode
    main(debug=False, mode=args.mode)
