"""
A module containing settings_helper functions
"""
import argparse
import asyncio
import copy
import dataclasses
import datetime
import inspect
import logging
import os.path
import pathlib
import colorama
from functools import wraps, partial, lru_cache
from typing import Union, Callable, Iterable, Any, AsyncIterator

from aiogram.utils.markdown import _join
from aiogram.utils.text_decorations import markdown_decoration


def parse_arguments() -> argparse.ArgumentParser.parse_args:
    """
    Parser for commandline arguments.
    :return: my_parser.parse_args()
    """
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument(
        "--debug",
        type=str2bool,
        action="store",
        const=True,
        nargs="?",
        required=False,
        default=False,
        help="If True, it prints everything set to DEBUG and above.",
    )
    my_parser.add_argument(
        "--test",
        type=str2bool,
        action="store",
        const=True,
        nargs="?",
        required=False,
        default=False,
        help="If True, the bot uses the TEST token.",
    )
    my_parser.add_argument(
        "--dbpass",
        type=str,
        action="store",
        const=True,
        nargs="?",
        required=True,
        default="changeit",
    )
    return my_parser.parse_args()


def str2bool(v: bool | int | str) -> bool:
    """
    Convert a string to a boolean argument
    https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
    """
    if isinstance(v, bool):
        return v
    elif isinstance(v, int):
        if v == 1:
            return True
        elif v == 0:
            return False
    elif v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean or equivalent value expected.")


def file_exists(dir_path: Union[str, os.PathLike], name: str) -> bool:
    """Returns true if the path exists"""
    path_to_name = pathlib.Path(os.path.join(dir_path, name))
    if path_to_name.exists():
        return True
    else:
        return False


def wrap_as_async(func) -> Callable:
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run


class LoggingFormatter(logging.Formatter):
    """A custom Formatter with colors for each logging level"""

    format = "%(levelname)s: %(name)s |  %(message)s"
    #
    FORMATS = {
        logging.DEBUG: f"{colorama.Fore.YELLOW}{format}{colorama.Style.RESET_ALL}",
        logging.INFO: f"{colorama.Fore.LIGHTGREEN_EX}{format}{colorama.Style.RESET_ALL}",
        logging.WARNING: f"{colorama.Fore.LIGHTRED_EX}{format}{colorama.Style.RESET_ALL}",
        logging.ERROR: f"{colorama.Fore.RED}{format}{colorama.Style.RESET_ALL}",
        logging.CRITICAL: f"{colorama.Fore.RED}{format}{format}{colorama.Style.RESET_ALL}",
    }

    def format(self, record) -> str:
        """See https://stackoverflow.com/a/384125"""
        record = copy.copy(record)
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def color_logging(level: int) -> logging.StreamHandler:
    """See https://docs.python.org/3/howto/logging-cookbook.html#logging-cookbook"""

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(level)
    # set a format which is simpler for console use
    formatter = LoggingFormatter()
    # tell the handler to use this format
    console.setFormatter(formatter)
    return console


@dataclasses.dataclass
class EnvVars:
    TOKEN_TELEGRAM_BOT = os.environ.get("TOKEN_TELEGRAM_BOT")
    TOKEN_TELEGRAM_BOT_TEST = os.environ.get("TOKEN_TELEGRAM_BOT_TEST")
    TOKEN_APIFY = os.environ.get("TOKEN_APIFY")


def func_name(frame) -> str:
    """Returns the name of the function passed"""
    return inspect.getframeinfo(frame)[2]


def log_func_name(thelogger: logging.getLogger, fun_name: str) -> None:
    """Logs the name of the function"""
    thelogger.debug(f"\t{fun_name}() called\n")


async def convert_iterable_to_async_iterator(iterable: Iterable[Any]) -> AsyncIterator[Any]:
    """Converts any iterable to Async iterator"""
    for i in iterable:
        yield i


def timed_lru_cache(minutes: int, maxsize: int = 12):
    """See https://realpython.com/lru-cache-python/"""

    def wrapper_cache(func):
        func = lru_cache(maxsize=maxsize)(func)

        func.lifetime = datetime.timedelta(minutes=minutes)

        func.expiration = datetime.datetime.utcnow() + func.lifetime

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if datetime.datetime.utcnow() >= func.expiration:
                func.cache_clear()

                func.expiration = datetime.datetime.utcnow() + func.lifetime

            return func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache


def escape_md(*content, sep=" ") -> str:
    """
    Escape markdown text
    """
    return markdown_decoration.quote(_join(*content, sep=sep))


def extract_schedule_id(message_text: str) -> str:
    """
    Extracts the schedule id from the text.

    For example:
        target_id='123456789.2a83b81d-0c5c-46a4-8607-ac1326ac61b2\ncategory: tpp\nSchedule news at 12:11:09 (Athens
            time)\nevery \n0 weeks | 1 days | 0 hours' becomes
        target_id='123456789.2a83b81d-0c5c-46a4-8607-ac1326ac61b2'
    """
    message_text = (
        message_text.split("\ncategory")
        if "category" in message_text
        else message_text.split("\nΚατηγορία")
    )
    target_id = message_text[0].replace("id:", "").strip()

    return target_id
