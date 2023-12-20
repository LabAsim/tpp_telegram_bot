import asyncio
import dataclasses
import inspect
import logging
import os
import traceback
from datetime import timedelta
from typing import Any, AsyncGenerator
from uuid import uuid4

from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from apscheduler import AsyncScheduler
from apscheduler.datastores.sqlalchemy import SQLAlchemyDataStore
from apscheduler.triggers.interval import IntervalTrigger

from src.db.funcs import construct_database_url
from src.helper.helper import log_func_name, func_name, convert_iterable_to_async_iterator

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class mock_message:
    text: str


async def get_postgres_engine() -> AsyncEngine:
    """
    :return: The postgres engine
    """
    log_func_name(thelogger=logger, fun_name=func_name(inspect.currentframe()))
    os.environ["database"] = "postgres"
    os.environ["dbpass"] = "Abcd1234"
    engine = create_async_engine(
        construct_database_url().replace("postgres://", "postgresql+asyncpg://")
    )
    return engine


async def start_scheduler_background(aiogram_dispatcher=None) -> None:
    """
    Starts the scheduler in the background.
    The while loop needs to exist to make sure the scheduler will never stop
    (if the func ends, the scheduler ends, too).
    """
    log_func_name(thelogger=logger, fun_name=func_name(inspect.currentframe()))
    engine = await get_postgres_engine()
    data_store = SQLAlchemyDataStore(engine)
    # This needs to be in a loop so as the scheduler no to exit the with block.
    # Modified from SO
    # (https://stackoverflow.com/questions/69939800/run-a-function-every-n-seconds-in-python-with-asyncio)
    while True:
        async with AsyncScheduler(
            data_store=data_store, cleanup_interval=timedelta(seconds=10)
        ) as scheduler:
            await scheduler.start_in_background()
            await asyncio.sleep(10)


async def start_scheduler_as_task(aiogram_dispatcher=None) -> None:
    """
    The scheduler needs to be created as a task to run along (and not to block)
    the other coroutines
    """
    log_func_name(thelogger=logger, fun_name=func_name(inspect.currentframe()))
    logging.info(f"event: {aiogram_dispatcher}")
    loop = asyncio.get_event_loop()
    loop.create_task(start_scheduler_background(aiogram_dispatcher))


async def schedule_target_rss_feed(chat_id: int, target_rss: str) -> None:
    log_func_name(thelogger=logger, fun_name=func_name(inspect.currentframe()))
    # To avoid circular imports
    from src.bot.bot_functions import send_rssfeed

    await send_rssfeed(message=None, chat_id=chat_id, target_rss=target_rss)


async def schedule_rss_feed(
    chat_id: str | int, target_rss: str, trigger_target: CronTrigger | IntervalTrigger
) -> None:
    """
    Adds the proposed rss schedule to the database.
    The id of the schedule is composed by a random number and the user's id.
    """
    log_func_name(thelogger=logger, fun_name=func_name(inspect.currentframe()))
    engine = create_async_engine(
        construct_database_url().replace("postgres://", "postgresql+asyncpg://")
    )
    logger.debug(f"postgres engine: {engine.engine}")
    data_store = SQLAlchemyDataStore(engine)

    try:
        async with AsyncScheduler(data_store) as scheduler:
            await scheduler.add_schedule(
                func_or_task_id=schedule_target_rss_feed,
                args=[chat_id, target_rss],
                trigger=trigger_target,
                id=f"{chat_id}.{str(uuid4())}",
            )
    except Exception:
        logger.warning(traceback.print_exc())


async def get_my_schedules(schedule_ids: list[Any]) -> AsyncGenerator:
    """Fetches the schedules info from the db"""
    engine = create_async_engine(
        construct_database_url().replace("postgres://", "postgresql+asyncpg://")
    )
    data_store = SQLAlchemyDataStore(engine)

    async with AsyncScheduler(data_store) as scheduler:
        async for schedule_id in convert_iterable_to_async_iterator(schedule_ids):
            yield scheduler.get_schedule(id=schedule_id["id"])
