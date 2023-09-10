from aiogram import Bot, types

from saved_tokens import TOKEN_TELEGRAM_BOT, TOKEN_TELEGRAM_BOT_TEST


def botify(
    token: str,
    mode: str,
    parse_mode=types.ParseMode.MARKDOWN_V2,
    timeout: int = 180,
    proxy_url: str = "http://proxy.server:3128",
) -> Bot:
    """Creates and returns the Bot object"""
    # Create the bot
    if mode == "pythonanywhere":
        # The proxy is needed only if the Bot is used on pythonanywhere.com
        bot_to_return = Bot(token=token, parse_mode=parse_mode, timeout=timeout, proxy=proxy_url)
    else:
        bot_to_return = Bot(token=token, parse_mode=parse_mode, timeout=timeout)
    return bot_to_return


def choose_token(debug: bool = False) -> str:
    """Re-parses the debug argument and returns the telegram token"""

    if debug:
        return TOKEN_TELEGRAM_BOT_TEST
    else:
        return TOKEN_TELEGRAM_BOT
