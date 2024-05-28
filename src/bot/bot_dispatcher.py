from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

try:
    import saved_tokens
except ModuleNotFoundError:
    from src.helper.helper import EnvVars as saved_tokens


def botify(
    token: str,
    parse_mode=ParseMode.MARKDOWN_V2,
) -> Bot:
    """Creates and returns the Bot object"""
    default_props = DefaultBotProperties(parse_mode=parse_mode)
    bot_to_return = Bot(token=token, default=default_props)

    return bot_to_return


def choose_token(test: bool = True) -> str:
    """Re-parses the debug argument and returns the telegram token"""

    if test:
        return saved_tokens.TOKEN_TELEGRAM_BOT_TEST
    else:
        return saved_tokens.TOKEN_TELEGRAM_BOT
