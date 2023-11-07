from aiogram import Bot, types

try:
    import saved_tokens
except ModuleNotFoundError:
    from source.helper.helper import EnvVars as saved_tokens


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


def choose_token(test: bool = True) -> str:
    """Re-parses the debug argument and returns the telegram token"""

    if test:
        return saved_tokens.TOKEN_TELEGRAM_BOT_TEST
    else:
        return saved_tokens.TOKEN_TELEGRAM_BOT
