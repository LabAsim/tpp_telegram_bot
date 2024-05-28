import logging
import asyncpg
import colorama
import pytest
from aiogram import types
from pydantic import BaseModel

from src.db.funcs import delete_user_info, construct_database_url
from unittest.mock import AsyncMock
import saved_tokens
from src.helper.helper import color_logging


@pytest.mark.asyncio
async def test_delete_user_info():
    class MockedUserId(BaseModel):
        """Mocks the User class from the from_user attribute of types.Message"""

        id: int = 12345678

    # This is needed just to import and use saved_tokens, so as the linter not to remove
    # the imported saved_tokens. In saved tokens, the dbpass is set in the os.environ
    saved_tokens.mock = ""
    # Insert a mock user
    database_url = construct_database_url()
    conn = await asyncpg.connect(dsn=database_url)
    try:
        await conn.execute("""INSERT INTO users(id,name,lang) VALUES(12345678,'geia','English');""")
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
