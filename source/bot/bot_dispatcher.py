# from main import debug
from aiogram import Bot, Dispatcher, executor, types

from config import DEBUG
from saved_tokens import TOKEN_APIFY, TOKEN_TELEGRAM_BOT, TOKEN_TELEGRAM_BOT_TEST
from source.bot.botvalues import BotConstructor
from source.helper.misc import PROXY_URL_PYTHONANYWHERE


def botify(token: str, parse_mode=types.ParseMode.MARKDOWN_V2, timeout: int = 180,
           proxy_url: str = "http://proxy.server:3128", debug: bool = False) -> Bot:
    """Creates and returns the Bot object"""
    # Create the bot
    if not debug:
        # The proxy is needed only if the Bot is used on pythonanywhere.com
        bot_to_return = Bot(token=token, parse_mode=parse_mode,
                            timeout=timeout, proxy=proxy_url)
    else:
        bot_to_return = Bot(token=token, parse_mode=parse_mode,
                            timeout=timeout)
    return bot_to_return


def choose_token() -> str:
    """Re-parses the debug argument and returns the telegram token"""
    #args = parse_arguments()
    #debug = args.debug
    if DEBUG:
        return TOKEN_TELEGRAM_BOT_TEST
    else:
        return TOKEN_TELEGRAM_BOT


bot = botify(token=choose_token(), proxy_url=PROXY_URL_PYTHONANYWHERE, debug=True)

dp = Dispatcher(bot)

_bot = BotConstructor(telegram_token=choose_token(), apify_token=TOKEN_APIFY, dispatcher=dp)
