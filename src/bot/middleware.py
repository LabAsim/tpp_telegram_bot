"""Custom Middlewares"""
import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

import src.db.funcs

logger = logging.getLogger(__name__)
logger.info(f"{__name__} imported")


class CounterMiddleware(BaseMiddleware):
    """
    See https://docs.aiogram.dev/en/latest/dispatcher/middlewares.html
    It needs to be registered in the main.
    For example:
        bot.session.middleware(CounterMiddleware())
    """

    def __init__(self) -> None:
        self.counter = 0

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        logger.info(f"{event=}")
        logger.info(f"{handler=}")
        logger.info(f"{data=}")
        self.counter += 1
        # data['counter'] = self.counter
        logger.info(f"counter: {self.counter}")
        return await handler(event, data)


class UserUpdateMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        await src.db.funcs.update_user_info(message=event)
        logger.debug("User info updated in db")
        return await handler(event, data)


# @dp.message.outer_middleware()
async def update_user_middleware(
    handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
    message: Message,
    data: Dict[str, Any],
) -> Any:
    """
    An outer middleware.
    Whenever a user sends a message,
    it updates the user data in the db.
    See: https://docs.aiogram.dev/en/latest/dispatcher/middlewares.html
    """
    # logger.info(f"{message=}")=
    # logger.info(f"{handler=}")
    # logger.info(f"{data=}")
    await src.db.funcs.update_user_info(message=message)
    logger.debug(f"{message.from_user} info updated")
    return await handler(message, data)
