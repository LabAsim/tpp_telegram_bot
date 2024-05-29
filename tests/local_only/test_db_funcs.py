import datetime
import logging
import asyncpg
import colorama
import pytest
from aiogram import types
from apscheduler.triggers.interval import IntervalTrigger
from pydantic import BaseModel

from src.db.funcs import (
    delete_user_info,
    construct_database_url,
    delete_all_user_schedules,
    delete_all_user_schedules_and_info,
)
from unittest.mock import AsyncMock
import saved_tokens
from src.helper.helper import color_logging
from src.scheduler.funcs import SchedulerSingleton, schedule_category


class MockedUserId(BaseModel):
    """Mocks the User class from the from_user attribute of types.Message"""

    id: int = 12345678


@pytest.mark.asyncio
async def test_delete_user_info():
    # This is needed just to import and use saved_tokens, so as the linter not to remove
    # the imported saved_tokens. In saved tokens, the dbpass is set in the os.environ
    saved_tokens.mock = ""
    # Insert a mock user
    database_url = construct_database_url()
    conn = await asyncpg.connect(dsn=database_url)
    try:
        await conn.execute(
            """INSERT INTO users(id,name,lang) VALUES($1,$2,$3);""",
            int(MockedUserId().id),
            "geia",
            "English",
        )
    except asyncpg.exceptions.UniqueViolationError:
        pass

    console = color_logging(level=logging.DEBUG)
    logging.basicConfig(
        level=logging.DEBUG,
        force=True,
        handlers=[console],
    )
    colorama.init(convert=True)

    # Pass a mocked message
    mock = AsyncMock(spec=types.Message)
    # See https://realpython.com/python-mock-library/#configuring-your-mock
    mock.from_user = MockedUserId()
    results = await delete_user_info(mock)
    assert results is True

    # The user is already deleted
    results = await delete_user_info(mock)
    assert results is False


@pytest.mark.asyncio
async def test_delete_all_user_schedules():
    # This is needed just to import and use saved_tokens, so as the linter not to remove
    # the imported saved_tokens. In saved tokens, the dbpass is set in the os.environ
    saved_tokens.mock = ""
    # Insert a mock user
    database_url = construct_database_url()
    await asyncpg.connect(dsn=database_url)

    # A fake schedule
    await schedule_category(
        chat_id=MockedUserId().id,
        target="tpp",
        scheduled_type="rss",
        trigger_target=IntervalTrigger(
            days=100,
            start_date=datetime.datetime.now(datetime.timezone.utc),
        ),
    )

    await schedule_category(
        chat_id=MockedUserId().id,
        target="ert",
        scheduled_type="rss",
        trigger_target=IntervalTrigger(
            days=100,
            start_date=datetime.datetime.now(datetime.timezone.utc),
        ),
    )

    console = color_logging(level=logging.DEBUG)
    logging.basicConfig(
        level=logging.DEBUG,
        force=True,
        handlers=[console],
    )
    colorama.init(convert=True)

    # Pass a mocked message
    mock = AsyncMock(spec=types.Message)
    # See https://realpython.com/python-mock-library/#configuring-your-mock
    mock.from_user = MockedUserId()

    # The scheduler needs to be initiated in order the test to work properly
    scheduler = SchedulerSingleton.get_scheduler()
    scheduler.start(paused=True)

    results = await delete_all_user_schedules(message=mock)
    assert results is True

    # The schedules is already deleted
    results = await delete_all_user_schedules(message=mock)
    logging.info(f"{results=}")
    assert results is False


@pytest.mark.asyncio
async def test_delete_all_user_schedules_and_info():
    # This is needed just to import and use saved_tokens, so as the linter not to remove
    # the imported saved_tokens. In saved tokens, the dbpass is set in the os.environ
    saved_tokens.mock = ""
    # Insert a mock user
    database_url = construct_database_url()
    conn = await asyncpg.connect(dsn=database_url)

    try:
        await conn.execute(
            """INSERT INTO users(id,name,lang) VALUES($1,$2,$3);""",
            int(MockedUserId().id),
            "geia",
            "English",
        )
    except asyncpg.exceptions.UniqueViolationError:
        pass

    # A fake schedule
    await schedule_category(
        chat_id=MockedUserId().id,
        target="tpp",
        scheduled_type="rss",
        trigger_target=IntervalTrigger(
            days=100,
            start_date=datetime.datetime.now(datetime.timezone.utc),
        ),
    )

    await schedule_category(
        chat_id=MockedUserId().id,
        target="ert",
        scheduled_type="rss",
        trigger_target=IntervalTrigger(
            days=100,
            start_date=datetime.datetime.now(datetime.timezone.utc),
        ),
    )

    console = color_logging(level=logging.DEBUG)
    logging.basicConfig(
        level=logging.DEBUG,
        force=True,
        handlers=[console],
    )
    colorama.init(convert=True)

    # Pass a mocked message
    mock = AsyncMock(spec=types.Message)
    # See https://realpython.com/python-mock-library/#configuring-your-mock
    mock.from_user = MockedUserId()

    # The scheduler needs to be initiated in order the test to work properly
    scheduler = SchedulerSingleton.get_scheduler()
    scheduler.start(paused=True)

    results = await delete_all_user_schedules_and_info(message=mock)
    assert results is True

    # The schedules is already deleted
    results = await delete_all_user_schedules_and_info(message=mock)
    logging.info(f"{results=}")
    assert results is False
