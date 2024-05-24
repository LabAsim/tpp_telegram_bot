import asyncio
import inspect
import logging
import os
import traceback
from typing import Any, AsyncGenerator
from uuid import uuid4

import pytz
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import create_engine, Engine
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.executors.pool import ProcessPoolExecutor

from src.db.funcs import construct_database_url
from src.helper.helper import log_func_name, func_name, convert_iterable_to_async_iterator

logger = logging.getLogger(__name__)


class SchedulerSingleton:
    """Initialize the scheduler"""

    instance = None

    @staticmethod
    def _create_scheduler():
        """Creates and returns a scheduler"""
        engine = get_postgres_engine()
        data_store = SQLAlchemyJobStore(engine=engine)
        # This needs to be in a loop so as the scheduler no to exit the with block.
        # Modified from SO
        # (https://stackoverflow.com/questions/69939800/run-a-function-every-n-seconds-in-python-with-asyncio)

        jobstores = {"postgres": data_store, "postgresql": data_store}
        executors = {
            # See here https://stackoverflow.com/q/77930656
            "default": AsyncIOExecutor(),
            "processpool": ProcessPoolExecutor(5),
        }
        job_defaults = {"coalesce": False, "max_instances": 3}
        scheduler = AsyncIOScheduler(
            jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=pytz.utc
        )
        logger.debug("created")
        return scheduler

    @staticmethod
    def get_scheduler():
        """
        Initializes a scheduler if it does not exist and returns it.
        """
        if SchedulerSingleton.instance is None:
            SchedulerSingleton.instance = SchedulerSingleton._create_scheduler()
        logger.debug("Fetching scheduler")
        return SchedulerSingleton.instance


def get_postgres_engine() -> Engine:
    """
    :return: The postgres engine
    """
    log_func_name(thelogger=logger, fun_name=func_name(inspect.currentframe()))
    os.environ["database"] = "postgres"
    os.environ["dbpass"] = "Abcd1234"
    # engine = create_async_engine(
    #     # https://stackoverflow.com/a/64698899
    #     construct_database_url().replace("postgres://", "postgresql+asyncpg://")
    # )
    engine = create_engine(construct_database_url().replace("postgres://", "postgresql://"))

    return engine


async def start_scheduler_background(aiogram_dispatcher=None) -> None:
    """
    Starts the scheduler in the background.
    """
    log_func_name(thelogger=logger, fun_name=func_name(inspect.currentframe()))
    SchedulerSingleton().get_scheduler().start()


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
    chat_id: str | int,
    target_rss: str,
    trigger_target: CronTrigger | IntervalTrigger,
    scheduled_type: str,
) -> None:
    """
    Adds the proposed rss schedule to the database.
    The id of the schedule is composed by a random number and the user's id.
    """
    log_func_name(thelogger=logger, fun_name=func_name(inspect.currentframe()))
    scheduler = SchedulerSingleton.get_scheduler()

    try:
        scheduler.add_job(
            jobstore="postgresql",
            func=schedule_target_rss_feed,
            args=[chat_id, target_rss],
            trigger=trigger_target,
            id=f"{chat_id}.{scheduled_type}.{target_rss}.{str(uuid4())}",
            replace_existing=True,
        )
    except Exception:
        logger.warning(traceback.print_exc())


async def schedule_target_search(chat_id: int, target: str) -> None:
    log_func_name(thelogger=logger, fun_name=func_name(inspect.currentframe()))
    # To avoid circular imports
    from src.bot.bot_functions import search

    # There is no user message, just a scheduled search scraping
    await search(message=None, chat_id=chat_id, target=target)


async def schedule_search(
    chat_id: str | int,
    target: str,
    trigger_target: CronTrigger | IntervalTrigger,
    scheduled_type: str,
) -> None:
    """
    Adds the proposed category to the database.
    The id of the schedule is composed by a random number and the user's id.
    """
    log_func_name(thelogger=logger, fun_name=func_name(inspect.currentframe()))
    scheduler = SchedulerSingleton.get_scheduler()
    try:
        scheduler.add_job(
            jobstore="postgresql",
            func=schedule_target_search,
            args=[chat_id, target],
            trigger=trigger_target,
            id=f"{chat_id}.{scheduled_type}.{target}.{str(uuid4())}",
            # id=f"{chat_id}.{str(uuid4())}",
            replace_existing=True,
        )
        logger.debug("Schedule added")
    except Exception:
        logger.warning(traceback.print_exc())


async def schedule_target_category(chat_id: int, target: str) -> None:
    log_func_name(thelogger=logger, fun_name=func_name(inspect.currentframe()))
    # To avoid circular imports
    from src.bot.bot_functions import search_category

    # There is no user message, just a scheduled category scraping
    await search_category(message=None, chat_id=chat_id, target=target)


async def schedule_category(
    chat_id: str | int,
    target: str,
    trigger_target: CronTrigger | IntervalTrigger,
    scheduled_type: str,
) -> None:
    """
    Adds the proposed category to the database.
    The id of the schedule is composed by a random number and the user's id.
    """
    log_func_name(thelogger=logger, fun_name=func_name(inspect.currentframe()))
    scheduler = SchedulerSingleton.get_scheduler()
    try:
        scheduler.add_job(
            jobstore="postgresql",
            func=schedule_target_category,
            args=[chat_id, target],
            trigger=trigger_target,
            # trigger=IntervalTrigger(
            #     seconds=10,
            #     start_date=datetime.datetime.now(datetime.timezone.utc),
            # ),
            id=f"{chat_id}.{scheduled_type}.{target}.{str(uuid4())}",
            replace_existing=True,
        )
        logger.debug("Schedule added")
    except Exception:
        logger.warning(traceback.print_exc())


async def get_my_schedules(schedule_ids: list[Any]) -> AsyncGenerator:
    """Fetches the schedules info from the db"""
    # engine = create_async_engine(
    #     construct_database_url().replace("postgres://", "postgresql+asyncpg://")
    # )
    # data_store = SQLAlchemyJobStore(engine=engine)
    scheduler = SchedulerSingleton.get_scheduler()
    for sc in schedule_ids:
        s = scheduler.get_job(job_id=sc["id"], jobstore="postgresql")
        logger.info(f"{s=}")
    async for schedule_id in convert_iterable_to_async_iterator(schedule_ids):
        yield scheduler.get_job(job_id=schedule_id["id"], jobstore="postgresql")
