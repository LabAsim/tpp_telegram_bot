import pytest
from aiogram.filters import Command
from aiogram_tests import MockedBot
from aiogram_tests.handler import MessageHandler
from aiogram_tests.types.dataset import MESSAGE

from src.bot.bot_functions import choose_language
import src.bot.commands_text


@pytest.mark.asyncio
async def test_choose_language_handler():
    commands = ["lang", "language", "start", "λανγ"]
    requester = MockedBot(MessageHandler(choose_language, Command(commands=commands)))
    for command in commands:
        calls = await requester.query(MESSAGE.as_object(text=f"/{command}"))
        print(calls)
        answer_message = calls.send_message.fetchone().text
        assert answer_message == src.bot.commands_text.Text.choose_lang_text


# It does not work currently!

# @pytest.mark.asyncio
# async def test_my_schedule():
#     commands = ["mysch", "myschedule", "μυσψη"]
#     requester = MockedBot(
#         MessageHandler(my_schedule, Command(commands=commands))
#     )
#     os.environ["dbpass"] = "Abcd1234"
#     for command in commands:
#         calls = await requester.query(
#             MESSAGE.as_object(
#                 text=f"/{command}",
#                 # from_user={
#                 #     "id": "12345678",
#                 #     "is_bot": False,
#                 #     "first_name": "random"
#                 # }
#             )
#         )
#         print(f"{calls=}")
#         answer_message = calls.send_message.fetchall()
#         print(f"{answer_message=}")
#         # assert answer_message == "asdadas"
