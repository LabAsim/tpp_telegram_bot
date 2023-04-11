"""Tests for bot_functions.py"""
import argparse
import sys
import unittest
# sys.argv.append("--debug True")
from apify_actor.main import SearchTerm
from unittest.mock import AsyncMock, patch, MagicMock
from example_echo_handler import echo
from source.bot.apify_actor import synthesize_url
from source.bot.bot_functions import save_language, welcome, to_search_next_page, search_next_page, _bot
from aiogram import md, types
from saved_tokens import token_apify, token_telegram_bot_test

t = {"message_id": 269, ' \
    '"from": {"id": 717353346, "is_bot": False, "first_name": "lam", "language_code": "en"}, ' \
    '"chat": {"id": 717353346, "first_name": "lam", "type": "private"}, ' \
    '"date": 1679935619, "text": "/lang", "entities": [{"type": "bot_command", "offset": 0, "length": 5}]}


class TestBot(unittest.IsolatedAsyncioTestCase):

    # def setUpClass(cls) -> None:
    #    cls.bot = BotConstructor(telegram_token=token_telegram_bot_test, apify_token=token_apify, test=True)
    # @patch('argparse.ArgumentParser.parse_args',
    #       return_value=argparse.Namespace(debug=True))\
    @classmethod
    def setUpClass(self) -> None:
        """Sets up the arbitrary user preferences"""
        _bot.settings["1234"] = {"lang": "Greek"}
        # _bot.save_all_settings()

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Delete all arbitrary settings
        """
        del _bot.settings["1234"]
        _bot.overwrite_save_settings()

        to_be_deleted = []

        for key in _bot.settings.keys():
            if "MagicMock" in key:
                to_be_deleted.append(key)

        for key in to_be_deleted:
            del _bot.settings[key]
            _bot.overwrite_save_settings()

    async def test_echo(self):
        text_mock = "test123"
        message_mock = AsyncMock(text=text_mock)
        await echo(message=message_mock)
        print(message_mock.answer)
        message_mock.answer.assert_called_with(text_mock)

    async def test_save_language_english(self):
        text_mock = "English 👍"
        message_mock = AsyncMock(text=text_mock)
        # print(message_mock.text)
        await save_language(message=message_mock)
        # print(message_mock.answer)
        answer = md.text(md.bold('\n👇 -- The command list -- 👇\n'),
                         '\n• /search or /s ',
                         md.escape_md('\n\n\t\t\tArticle search based on a keyword'),
                         '\n\n\t\t\tExample:\t/search ΒΙΟΜΕ',
                         '\n',
                         '\n• /category or /c  ',
                         md.escape_md('\n\n\t\t\tSearch the latest news of the category'),
                         md.escape_md('\n\n\t\t\tExample:\t/category Newsroom'),
                         md.escape_md('\n'),
                         '\n• /language or /lang',
                         md.escape_md('\n\n\t\t\tChoose your preferred language'),
                         md.escape_md('\n\n• /help : Prints this help text'),
                         '\n'
                         )
        message_mock.answer.assert_called_with(answer)

    async def test_save_lanugage_greek(self):
        text_mock = "Greek 🤝"
        message_mock = AsyncMock(text=text_mock)
        # print(message_mock.text)
        await save_language(message=message_mock)
        # print(message_mock.answer)
        answer = md.text(md.bold('\n👇 -- Η λίστα με όλες τις εντολές -- 👇\n'),
                         '\n• /search ή /s ',
                         md.escape_md('\n\n\t\t\tΑναζήτηση άρθρων βάσει λέξης κλειδί.'),
                         '\n\n\t\t\tΠαράδειγμα:\t/search ΒΙΟΜΕ',
                         '\n',
                         '\n• /category ή /c  ',
                         md.escape_md('\n\n\t\t\tΑναζήτηση τελευταίων άρθρων συγκεκριμένης κατηγορίας.'),
                         md.escape_md('\n\n\t\t\tΠαράδειγμα:\t/category Newsroom'),
                         md.escape_md('\n'),
                         '\n• /language ή /lang',
                         md.escape_md('\n\n\t\t\tΔιάλεξε τη γλώσσα της επιλογής σου'),
                         md.escape_md('\n\n• /help : Τυπώνει αυτό το βοηθητικό κείμενο'),
                         '\n'
                         )
        message_mock.answer.assert_called_with(answer)

    async def test_start_welcome(self):
        text_mock = "/start"
        message_mock = AsyncMock(text=text_mock)
        await welcome(message=message_mock)
        answer = md.escape_md('👋 Hello! Please select your language.'
                              '\n👋 Γεια! Διάλεξε τι γλώσσα επιλογής σου')

        # reply = message_mock.return_value
        # print(f"reply: {reply}")
        # {"keyboard": [[{"text": "English 👍"}], [{"text": "Greek 🤝"}]], "resize_keyboard": true, "one_time_keyboard": true}
        # Assert that the message sent to bot is "/start"
        self.assertEqual(message_mock.text, text_mock)
        # Assert that the text replied to user is the appropiate answer
        self.assertEqual(message_mock.answer.call_args.args[0], answer)
        self.assertIsInstance(message_mock.answer.call_args.kwargs["reply_markup"], types.ReplyKeyboardMarkup)
        # Assert that a reply Keyboard was passed to the user
        self.assertEqual(message_mock.answer.call_args.kwargs["reply_markup"].keyboard[0][0].text, "English 👍")
        self.assertEqual(message_mock.answer.call_args.kwargs["reply_markup"].keyboard[1][0].text, "Greek 🤝")
        # Assert the other options
        self.assertEqual(message_mock.answer.call_args.kwargs["reply_markup"].one_time_keyboard, True)
        self.assertEqual(message_mock.answer.call_args.kwargs["reply_markup"].resize_keyboard, True)

    async def ttest_help(self):
        pass

    async def test_choose_language(self):
        # /lang
        text_mock = "/lang"
        message_mock = AsyncMock(text=text_mock)
        await welcome(message=message_mock)
        answer = md.escape_md('👋 Hello! Please select your language.'
                              '\n👋 Γεια! Διάλεξε τι γλώσσα επιλογής σου')
        # Assert that the message sent to bot is "/start"
        self.assertEqual(message_mock.text, text_mock)
        # Assert that the text replied to user is the appropiate answer
        self.assertEqual(message_mock.answer.call_args.args[0], answer)
        self.assertIsInstance(message_mock.answer.call_args.kwargs["reply_markup"], types.ReplyKeyboardMarkup)
        # Assert that a reply Keyboard was passed to the user
        self.assertEqual(message_mock.answer.call_args.kwargs["reply_markup"].keyboard[0][0].text, "English 👍")
        self.assertEqual(message_mock.answer.call_args.kwargs["reply_markup"].keyboard[1][0].text, "Greek 🤝")
        # Assert the other options
        self.assertEqual(message_mock.answer.call_args.kwargs["reply_markup"].one_time_keyboard, True)
        self.assertEqual(message_mock.answer.call_args.kwargs["reply_markup"].resize_keyboard, True)

        # /language
        text_mock = "/language"
        message_mock = AsyncMock(text=text_mock)
        await welcome(message=message_mock)
        answer = md.escape_md('👋 Hello! Please select your language.'
                              '\n👋 Γεια! Διάλεξε τι γλώσσα επιλογής σου')
        # Assert that the message sent to bot is "/start"
        self.assertEqual(message_mock.text, text_mock)
        # Assert that the text replied to user is the appropiate answer
        self.assertEqual(message_mock.answer.call_args.args[0], answer)
        self.assertIsInstance(message_mock.answer.call_args.kwargs["reply_markup"], types.ReplyKeyboardMarkup)
        # Assert that a reply Keyboard was passed to the user
        self.assertEqual(message_mock.answer.call_args.kwargs["reply_markup"].keyboard[0][0].text, "English 👍")
        self.assertEqual(message_mock.answer.call_args.kwargs["reply_markup"].keyboard[1][0].text, "Greek 🤝")
        # Assert the other options
        self.assertEqual(message_mock.answer.call_args.kwargs["reply_markup"].one_time_keyboard, True)
        self.assertEqual(message_mock.answer.call_args.kwargs["reply_markup"].resize_keyboard, True)

    async def test_to_search_next_page(self):
        text_mock = "arbitrary text, it does not mean anything"
        message_mock = AsyncMock(text=text_mock)
        dict_for_message_mock = {"from": {"id": "1234"}}
        message_mock.__getitem__.side_effect = dict_for_message_mock.__getitem__
        # English lang for this test user
        _bot.settings["1234"] = {"lang": "English"}
        await to_search_next_page(message=message_mock)
        answer = "Do you want to search the next page?"
        self.assertEqual(message_mock.text, text_mock)
        # Assert that the text replied to user is the appropriate answer
        self.assertEqual(message_mock.method_calls[0].args[0], answer)
        self.assertIsInstance(message_mock.method_calls[0].kwargs["reply_markup"], types.ReplyKeyboardMarkup)
        # Assert that a reply Keyboard was passed to the user
        self.assertEqual(message_mock.method_calls[0].kwargs["reply_markup"].keyboard[0][0], "Yes 🆗")
        self.assertEqual(message_mock.method_calls[0].kwargs["reply_markup"].keyboard[0][1], "No 👎")
        # Assert the other options
        self.assertEqual(message_mock.method_calls[0].kwargs["reply_markup"].one_time_keyboard, None)
        self.assertEqual(message_mock.method_calls[0].kwargs["reply_markup"].resize_keyboard, True)
        self.assertEqual(message_mock.method_calls[0].kwargs["reply_markup"].selective, True)
        self.assertEqual(message_mock.method_calls[0].kwargs["reply_markup"].is_persistent, None)

        # Greek lang for this test user
        text_mock = "arbitrary text, it does not mean anything"
        message_mock = AsyncMock(text=text_mock)
        dict_for_message_mock = {"from": {"id": "1234"}}
        message_mock.__getitem__.side_effect = dict_for_message_mock.__getitem__
        _bot.settings["1234"] = {"lang": "Greek"}
        await to_search_next_page(message=message_mock)
        answer = "Θέλετε να συνεχίσετε την αναζήτηση στην επόμενη σελίδα;"
        self.assertEqual(message_mock.text, text_mock)
        # Assert that the text replied to user is the appropriate answer
        self.assertEqual(message_mock.method_calls[0].args[0], answer)
        self.assertIsInstance(message_mock.method_calls[0].kwargs["reply_markup"], types.ReplyKeyboardMarkup)
        # Assert that a reply Keyboard was passed to the user
        self.assertEqual(message_mock.method_calls[0].kwargs["reply_markup"].keyboard[0][0], "Ναι 🆗")
        self.assertEqual(message_mock.method_calls[0].kwargs["reply_markup"].keyboard[0][1], "Όχι 👎")
        # Assert the other options
        self.assertEqual(message_mock.method_calls[0].kwargs["reply_markup"].one_time_keyboard, None)
        self.assertEqual(message_mock.method_calls[0].kwargs["reply_markup"].resize_keyboard, True)
        self.assertEqual(message_mock.method_calls[0].kwargs["reply_markup"].selective, True)
        self.assertEqual(message_mock.method_calls[0].kwargs["reply_markup"].is_persistent, None)

    @patch.object(_bot, 'page_number', 1)
    async def test_search_next_page(self):
        """There is nothing to search and page number is 1"""

        # English lang
        text_mock = "Yes 🆗"
        message_mock = AsyncMock(text=text_mock)
        dict_for_message_mock = {"from": {"id": "1234"}}
        message_mock.__getitem__.side_effect = dict_for_message_mock.__getitem__
        _bot.settings["1234"] = {"lang": "English"}
        _bot.search_keyword = ""
        await search_next_page(message=message_mock)
        answer = md.escape_md("Nothing to search.\nRepeat the search command /search <keyword>")
        print(_bot.page_number, _bot.search_keyword)
        self.assertEqual(message_mock.method_calls[0].kwargs['text'], answer)
        self.assertEqual(message_mock.method_calls[0].kwargs['reply_markup'].remove_keyboard, True)
        self.assertEqual(message_mock.method_calls[0].kwargs['reply_markup'].selective, None)

        # Greek
        text_mock = "Ναι 🆗"
        message_mock = AsyncMock(text=text_mock)
        dict_for_message_mock = {"from": {"id": "1234"}}
        message_mock.__getitem__.side_effect = dict_for_message_mock.__getitem__
        _bot.settings["1234"] = {"lang": "Greek"}
        _bot.search_keyword = ""
        await search_next_page(message=message_mock)
        answer = md.escape_md("\nΕπαναλάβετε την αναζήτηση με την εντολή /search <λέξη κλειδί>")
        self.assertEqual(message_mock.method_calls[0].kwargs['text'], answer)
        self.assertEqual(message_mock.method_calls[0].kwargs['reply_markup'].remove_keyboard, True)
        self.assertEqual(message_mock.method_calls[0].kwargs['reply_markup'].selective, None)

    @patch.object(_bot, 'page_number', 1)
    @patch.object(_bot, 'search_keyword', 'Mitsotakis')
    async def test_search_next_page1(self):
        """Assert that the data sent to the user is the desired one.
        Tests the default page number and a keyword"""
        # Scrape the titles + urls directly, without calling the apify actor
        url = synthesize_url(keyword="Mitsotakis", page_number=1)
        search_results = SearchTerm(final_url=url, debug=False)
        dict_from_search_results = {}
        for _dataclass in search_results.list:
            dict_from_search_results[_dataclass.title] = _dataclass.url
        # Transform the results dict to the same format as the one pushed to the user (in telegram markdown)
        answer = md.text()
        for result_dict_key in list(dict_from_search_results.keys()):
            title = result_dict_key
            url = dict_from_search_results[result_dict_key]
            last_line = ("-" * 50)
            answer += md.text(
                md.text(""),
                md.bold((md.text(title))),
                md.text(md.escape_md(url)),
                md.text(md.escape_md(last_line)), sep="\n")
        # Mocked message
        text_mock = "Yes"
        message_mock = AsyncMock(text=text_mock)
        dict_for_message_mock = {"from": {"id": "1234"}}
        message_mock.__getitem__.side_effect = dict_for_message_mock.__getitem__
        _bot.settings["1234"] = {"lang": "Greek"}
        print(f"\nnumber: {_bot.page_number}, keyword:{_bot.search_keyword}")
        # call the bot method for scraping (using the apify actor)
        await search_next_page(message=message_mock)
        # Assert that the bot replies the same as the `answer`,
        # which contains the titles+urls that we have scraped above.
        self.assertEqual(len(message_mock.method_calls[0].args[0]), len(answer))

        for result_dict_key in list(dict_from_search_results.keys()):
            title = result_dict_key
            url = dict_from_search_results[result_dict_key]
            last_line = ("-" * 50)
            single_answer = md.text(
                md.text(""),
                md.bold((md.text(title))),
                md.text(md.escape_md(url)),
                md.text(md.escape_md(last_line)), sep="\n")
            # Assert that the `single_answer` string exists in `answer`
            temp_answer = message_mock.method_calls[0].args[0]
            self.assertTrue(single_answer in temp_answer)

        self.assertEqual(message_mock.method_calls[0].kwargs['reply_markup'].remove_keyboard, True)
        self.assertEqual(message_mock.method_calls[0].kwargs['reply_markup'].selective, None)

    @patch.object(_bot, 'page_number', 2)
    @patch.object(_bot, 'search_keyword', 'Τσιπρας')
    async def test_search_next_page2(self):
        """Assert that the data sent to the user is the desired one.
        Tests a non-default page number and a keyword"""
        # Scrape the titles + urls directly, without calling the apify actor
        url = synthesize_url(keyword="Τσιπρας", page_number=2)
        search_results = SearchTerm(final_url=url, debug=False)
        dict_from_search_results = {}
        for _dataclass in search_results.list:
            dict_from_search_results[_dataclass.title] = _dataclass.url
        # Transform the results dict to the same format as the one pushed to the user (in telegram markdown)
        answer = md.text()
        for result_dict_key in list(dict_from_search_results.keys()):
            title = result_dict_key
            url = dict_from_search_results[result_dict_key]
            last_line = ("-" * 50)
            answer += md.text(
                md.text(""),
                md.bold((md.text(title))),
                md.text(md.escape_md(url)),
                md.text(md.escape_md(last_line)), sep="\n")
        # Mocked message
        text_mock = "Yes"
        message_mock = AsyncMock(text=text_mock)
        dict_for_message_mock = {"from": {"id": "1234"}}
        message_mock.__getitem__.side_effect = dict_for_message_mock.__getitem__
        # English lang for this test user
        _bot.settings["1234"] = {"lang": "English"}
        print(f"\nnumber: {_bot.page_number}, keyword:{_bot.search_keyword}")
        # call the bot method for scraping (using the apify actor)
        await search_next_page(message=message_mock)
        # Assert that the bot replies the same as the `answer`,
        # which contains the titles+urls that we have scraped above.
        # self.assertEqual(len(message_mock.method_calls[0].args[0]), len(answer))
        # There is a possibility that the items in the `answer` and the message_mock are not ordered in the same way.
        # Assert that each item in `answer` exists in `message_mock.method_calls[0].args[0]`
        for result_dict_key in list(dict_from_search_results.keys()):
            title = result_dict_key
            url = dict_from_search_results[result_dict_key]
            last_line = ("-" * 50)
            single_answer = md.text(
                md.text(""),
                md.bold((md.text(title))),
                md.text(md.escape_md(url)),
                md.text(md.escape_md(last_line)), sep="\n")
            # Assert that the `single_answer` string exists in `answer`
            temp_answer = message_mock.method_calls[0].args[0]
            self.assertTrue(single_answer in temp_answer)
        # self.assertEqual(message_mock.method_calls[0].args[0], answer)
        self.assertEqual(message_mock.method_calls[0].kwargs['reply_markup'].remove_keyboard, True)
        self.assertEqual(message_mock.method_calls[0].kwargs['reply_markup'].selective, None)

    @patch.object(_bot, 'page_number', 1)
    @patch.object(_bot, 'search_keyword', '')
    async def test_search_next_page3(self):
        """
        Tests a non-default page number and a empty string as the search keyword.
        If there is not a keyword, the url should return `""`"""
        # Mocked message
        text_mock = "Yes"
        message_mock = AsyncMock(text=text_mock)
        dict_for_message_mock = {"from": {"id": "1234"}}
        message_mock.__getitem__.side_effect = dict_for_message_mock.__getitem__
        # English lang for this test user
        _bot.settings["1234"] = {"lang": "English"}
        print(f"\nnumber: {_bot.page_number}, keyword:{_bot.search_keyword}")
        # call the bot method for scraping (using the apify actor)
        await search_next_page(message=message_mock)
        self.assertEqual(message_mock.method_calls[0].kwargs['text'], "Nothing to search\\.\nRepeat the search command "
                                                                      "/search <keyword\\>")
        self.assertEqual(message_mock.method_calls[0].kwargs['reply_markup'].remove_keyboard, True)
        self.assertEqual(message_mock.method_calls[0].kwargs['reply_markup'].selective, None)

        # Mocked message
        text_mock = "Yes"
        message_mock = AsyncMock(text=text_mock)
        dict_for_message_mock = {"from": {"id": "1234"}}
        message_mock.__getitem__.side_effect = dict_for_message_mock.__getitem__
        # English lang for this test user
        _bot.settings["1234"] = {"lang": "English"}
        print(f"\nnumber: {_bot.page_number}, keyword:{_bot.search_keyword}")
        # call the bot method for scraping (using the apify actor)
        await search_next_page(message=message_mock)
        self.assertEqual(message_mock.method_calls[0].kwargs['text'], "Nothing to search\\.\nRepeat the search command "
                                                                      "/search <keyword\\>")
        self.assertEqual(message_mock.method_calls[0].kwargs['reply_markup'].remove_keyboard, True)
        self.assertEqual(message_mock.method_calls[0].kwargs['reply_markup'].selective, None)