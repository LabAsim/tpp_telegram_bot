import pytest
from aiogram.filters import Command
from aiogram_tests import MockedBot
from aiogram_tests.handler import MessageHandler
from aiogram_tests.types.dataset import MESSAGE

import src.bot.bot_functions
import src.bot.commands_text


@pytest.mark.asyncio
async def test_choose_language_handler():
    commands = ["lang", "language", "start", "λανγ"]
    requester = MockedBot(
        MessageHandler(src.bot.bot_functions.choose_language, Command(commands=commands))
    )
    for command in commands:
        calls = await requester.query(MESSAGE.as_object(text=f"/{command}"))
        print(calls)
        answer_message = calls.send_message.fetchone().text
        assert answer_message == src.bot.commands_text.Text.choose_lang_text
