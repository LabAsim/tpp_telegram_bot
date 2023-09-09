"""Tests for bot_functions.py"""
import unittest
from apify_actor.main import SearchTerm
from unittest.mock import AsyncMock, patch, MagicMock
from example_echo_handler import echo
from source.bot.apify_actor import synthesize_url, convert_category_str_to_url
from apify_actor.category_actor import CategoryScraper, _header
from source.bot.bot_functions import save_language, to_search_next_page, search_next_page, show_help, \
    choose_language, end_search, search, search_handler, search_category, settings_helper
from aiogram import md, types
from source.bot.commands_text import Text


class TestBot(unittest.IsolatedAsyncioTestCase):

    # def setUp(self) -> None:
    #     settings_helper = pass


    @classmethod
    def setUpClass(cls) -> None:
        """Sets up the arbitrary user preferences"""
        settings_helper.settings["1234"] = {"lang": "Greek"}

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Delete all arbitrary settings
        """
        del settings_helper.settings["1234"]
        settings_helper.overwrite_save_settings()

        to_be_deleted = []

        for key in settings_helper.settings.keys():
            if "MagicMock" in key:
                to_be_deleted.append(key)

        for key in to_be_deleted:
            del settings_helper.settings[key]
            settings_helper.overwrite_save_settings()

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
        answer = Text.help_text_eng
        message_mock.answer.assert_called_with(answer)

    async def test_save_language_greek(self):
        text_mock = "Greek 🤝"
        message_mock = AsyncMock(text=text_mock)

        await save_language(message=message_mock)

        answer = Text.help_text_greek
        message_mock.answer.assert_called_with(answer)

    async def test_help(self):
        """Test for the /help command"""
        # English help message
        text_mock = "/help"
        message_mock = AsyncMock(text=text_mock)
        dict_for_message_mock = {"from": {"id": "1234"}}
        message_mock.__getitem__.side_effect = dict_for_message_mock.__getitem__
        settings_helper.settings["1234"] = {"lang": "English"}
        settings_helper.search_keyword = ""
        await show_help(message=message_mock)
        answer = Text.help_text_eng
        self.assertEqual(message_mock.method_calls[0].args[0], answer)

        # Greek help message
        text_mock = "/help"
        message_mock = AsyncMock(text=text_mock)
        dict_for_message_mock = {"from": {"id": "1234"}}
        message_mock.__getitem__.side_effect = dict_for_message_mock.__getitem__
        settings_helper.settings["1234"] = {"lang": "Greek"}
        settings_helper.search_keyword = ""
        await show_help(message=message_mock)
        answer = Text.help_text_greek
        self.assertEqual(message_mock.method_calls[0].args[0], answer)

    async def test_choose_language(self):

        text_mock = "/start"
        message_mock = AsyncMock(text=text_mock)
        await choose_language(message=message_mock)
        answer = Text.choose_lang_text

        self.assertEqual(message_mock.text, text_mock)

        self.assertEqual(message_mock.answer.call_args.args[0], answer)
        self.assertIsInstance(message_mock.answer.call_args.kwargs["reply_markup"], types.ReplyKeyboardMarkup)

        self.assertEqual(message_mock.answer.call_args.kwargs["reply_markup"].keyboard[0][0].text, "English 👍")
        self.assertEqual(message_mock.answer.call_args.kwargs["reply_markup"].keyboard[1][0].text, "Greek 🤝")

        self.assertEqual(message_mock.answer.call_args.kwargs["reply_markup"].one_time_keyboard, True)
        self.assertEqual(message_mock.answer.call_args.kwargs["reply_markup"].resize_keyboard, True)

        text_mock = "/lang"
        message_mock = AsyncMock(text=text_mock)
        await choose_language(message=message_mock)
        answer = Text.choose_lang_text

        self.assertEqual(message_mock.text, text_mock)

        self.assertEqual(message_mock.answer.call_args.args[0], answer)
        self.assertIsInstance(message_mock.answer.call_args.kwargs["reply_markup"], types.ReplyKeyboardMarkup)

        self.assertEqual(message_mock.answer.call_args.kwargs["reply_markup"].keyboard[0][0].text, "English 👍")
        self.assertEqual(message_mock.answer.call_args.kwargs["reply_markup"].keyboard[1][0].text, "Greek 🤝")

        self.assertEqual(message_mock.answer.call_args.kwargs["reply_markup"].one_time_keyboard, True)
        self.assertEqual(message_mock.answer.call_args.kwargs["reply_markup"].resize_keyboard, True)

        # /language
        text_mock = "/language"
        message_mock = AsyncMock(text=text_mock)
        await choose_language(message=message_mock)
        answer = Text.choose_lang_text
        self.assertEqual(message_mock.text, text_mock)
        self.assertEqual(message_mock.answer.call_args.args[0], answer)
        self.assertIsInstance(message_mock.answer.call_args.kwargs["reply_markup"], types.ReplyKeyboardMarkup)

        self.assertEqual(message_mock.answer.call_args.kwargs["reply_markup"].keyboard[0][0].text, "English 👍")
        self.assertEqual(message_mock.answer.call_args.kwargs["reply_markup"].keyboard[1][0].text, "Greek 🤝")

        self.assertEqual(message_mock.answer.call_args.kwargs["reply_markup"].one_time_keyboard, True)
        self.assertEqual(message_mock.answer.call_args.kwargs["reply_markup"].resize_keyboard, True)

    async def test_search(self):
        """Tests the /search command"""
        # Scrape the titles + urls directly, without calling the apify actor
        url = synthesize_url(keyword="Τσιπρας", page_number=1)
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

        text_mock = "/search Τσιπρας"
        message_mock = AsyncMock(text=text_mock)
        dict_for_message_mock = {"from": {"id": "1234"}}
        message_mock.__getitem__.side_effect = dict_for_message_mock.__getitem__
        settings_helper.settings["1234"] = {"lang": "English"}

        await search(message=message_mock)

        self.assertEqual(settings_helper.page_number, 2)
        self.assertEqual(settings_helper.search_keyword, 'Τσιπρας')
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

    async def test_search_handler(self, ):

        text_mock = "/search Τσιπρας"
        message_mock = AsyncMock(text=text_mock)
        dict_for_message_mock = {"from": {"id": "1234"}}
        message_mock.__getitem__.side_effect = dict_for_message_mock.__getitem__

        settings_helper.settings["1234"] = {"lang": "English"}
        await search_handler(message=message_mock)

        self.assertEqual(message_mock.method_calls[1].args[0], Text.to_search_next_page_eng)
        self.assertEqual(message_mock.method_calls[1].kwargs['reply_markup'].keyboard[0][0], "Yes 🆗")
        self.assertEqual(message_mock.method_calls[1].kwargs['reply_markup'].keyboard[0][1], "No 👎")

        self.assertEqual(message_mock.method_calls[1].kwargs["reply_markup"].one_time_keyboard, None)
        self.assertEqual(message_mock.method_calls[1].kwargs["reply_markup"].resize_keyboard, True)
        self.assertEqual(message_mock.method_calls[1].kwargs["reply_markup"].selective, True)
        self.assertEqual(message_mock.method_calls[1].kwargs["reply_markup"].is_persistent, None)

        settings_helper.settings["1234"] = {"lang": "Greek"}
        await search_handler(message=message_mock)

        self.assertEqual(message_mock.method_calls[3].args[0], Text.to_search_next_page_greek)
        self.assertEqual(message_mock.method_calls[3].kwargs['reply_markup'].keyboard[0][0], "Ναι 🆗")
        self.assertEqual(message_mock.method_calls[3].kwargs['reply_markup'].keyboard[0][1], "Όχι 👎")

        self.assertEqual(message_mock.method_calls[3].kwargs["reply_markup"].one_time_keyboard, None)
        self.assertEqual(message_mock.method_calls[3].kwargs["reply_markup"].resize_keyboard, True)
        self.assertEqual(message_mock.method_calls[3].kwargs["reply_markup"].selective, True)
        self.assertEqual(message_mock.method_calls[3].kwargs["reply_markup"].is_persistent, None)

    async def test_to_search_next_page(self):
        text_mock = "arbitrary text, it does not mean anything"
        message_mock = AsyncMock(text=text_mock)
        dict_for_message_mock = {"from": {"id": "1234"}}
        message_mock.__getitem__.side_effect = dict_for_message_mock.__getitem__
        # English lang for this test user
        settings_helper.settings["1234"] = {"lang": "English"}
        await to_search_next_page(message=message_mock)
        answer = Text.to_search_next_page_eng
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
        settings_helper.settings["1234"] = {"lang": "Greek"}
        await to_search_next_page(message=message_mock)
        answer = Text.to_search_next_page_greek
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

    @patch.object(settings_helper, 'page_number', 1)
    async def test_search_next_page(self):
        """There is nothing to search and page number is 1"""

        # English lang
        text_mock = "Yes 🆗"
        message_mock = AsyncMock(text=text_mock)
        dict_for_message_mock = {"from": {"id": "1234"}}
        message_mock.__getitem__.side_effect = dict_for_message_mock.__getitem__
        settings_helper.settings["1234"] = {"lang": "English"}
        settings_helper.search_keyword = ""
        await search_next_page(message=message_mock)
        answer = Text.search_next_page_empty_keyword_page_no_1_eng
        print(settings_helper.page_number, settings_helper.search_keyword)
        self.assertEqual(message_mock.method_calls[0].kwargs['text'], answer)
        self.assertEqual(message_mock.method_calls[0].kwargs['reply_markup'].remove_keyboard, True)
        self.assertEqual(message_mock.method_calls[0].kwargs['reply_markup'].selective, None)

        # Greek
        text_mock = "Ναι 🆗"
        message_mock = AsyncMock(text=text_mock)
        dict_for_message_mock = {"from": {"id": "1234"}}
        message_mock.__getitem__.side_effect = dict_for_message_mock.__getitem__
        settings_helper.settings["1234"] = {"lang": "Greek"}
        settings_helper.search_keyword = ""
        await search_next_page(message=message_mock)
        answer = Text.search_next_page_empty_keyword_page_no_1_greek
        self.assertEqual(message_mock.method_calls[0].kwargs['text'], answer)
        self.assertEqual(message_mock.method_calls[0].kwargs['reply_markup'].remove_keyboard, True)
        self.assertEqual(message_mock.method_calls[0].kwargs['reply_markup'].selective, None)

    @patch.object(settings_helper, 'page_number', 1)
    @patch.object(settings_helper, 'search_keyword', 'Mitsotakis')
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
        text_mock = "Yes 🆗"
        message_mock = AsyncMock(text=text_mock)
        dict_for_message_mock = {"from": {"id": "1234"}}
        message_mock.__getitem__.side_effect = dict_for_message_mock.__getitem__
        settings_helper.settings["1234"] = {"lang": "Greek"}
        print(f"\nnumber: {settings_helper.page_number}, keyword:{settings_helper.search_keyword}")
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

    @patch.object(settings_helper, 'page_number', 2)
    @patch.object(settings_helper, 'search_keyword', 'Τσιπρας')
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
        settings_helper.settings["1234"] = {"lang": "English"}
        print(f"\nnumber: {settings_helper.page_number}, keyword:{settings_helper.search_keyword}")
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

    @patch.object(settings_helper, 'page_number', 1)
    @patch.object(settings_helper, 'search_keyword', '')
    async def test_search_next_page3(self):
        """
        Tests a non-default page number and a empty string as the search keyword.
        If there is not a keyword, the url should return `""`"""
        # English lang for this test user
        text_mock = "Yes"
        message_mock = AsyncMock(text=text_mock)
        dict_for_message_mock = {"from": {"id": "1234"}}
        message_mock.__getitem__.side_effect = dict_for_message_mock.__getitem__

        settings_helper.settings["1234"] = {"lang": "English"}
        print(f"\nnumber: {settings_helper.page_number}, keyword:{settings_helper.search_keyword}")
        # call the bot method for scraping (using the apify actor)
        await search_next_page(message=message_mock)
        self.assertEqual(message_mock.method_calls[0].kwargs['text'], Text.search_next_page_empty_keyword_page_no_1_eng)
        self.assertEqual(message_mock.method_calls[0].kwargs['reply_markup'].remove_keyboard, True)
        self.assertEqual(message_mock.method_calls[0].kwargs['reply_markup'].selective, None)

        # Greek lang
        text_mock = "Yes"
        message_mock = AsyncMock(text=text_mock)
        dict_for_message_mock = {"from": {"id": "1234"}}
        message_mock.__getitem__.side_effect = dict_for_message_mock.__getitem__

        settings_helper.settings["1234"] = {"lang": "Greek"}
        print(f"\nnumber: {settings_helper.page_number}, keyword:{settings_helper.search_keyword}")
        # call the bot method for scraping (using the apify actor)
        await search_next_page(message=message_mock)
        self.assertEqual(message_mock.method_calls[0].kwargs['text'],
                         Text.search_next_page_empty_keyword_page_no_1_greek)
        self.assertEqual(message_mock.method_calls[0].kwargs['reply_markup'].remove_keyboard, True)
        self.assertEqual(message_mock.method_calls[0].kwargs['reply_markup'].selective, None)

    @patch.object(settings_helper, 'search_keyword', 'Tsipras')
    async def test_end_search(self):

        # english
        text_mock = "No 👎"
        message_mock = AsyncMock(text=text_mock)
        dict_for_message_mock = {"from": {"id": "1234"}}
        message_mock.__getitem__.side_effect = dict_for_message_mock.__getitem__
        settings_helper.settings["1234"] = {"lang": "English"}
        await end_search(message=message_mock)

        self.assertEqual(f"Search for 'Tsipras' is ended", message_mock.method_calls[0].args[0])
        self.assertEqual(settings_helper.search_keyword, "")
        self.assertEqual(settings_helper.page_number, 1)

        # Greek
        text_mock = "Όχι 👎"
        message_mock = AsyncMock(text=text_mock)
        dict_for_message_mock = {"from": {"id": "1234"}}
        message_mock.__getitem__.side_effect = dict_for_message_mock.__getitem__
        settings_helper.settings["1234"] = {"lang": "Greek"}
        settings_helper.search_keyword = "Tsipras"
        await end_search(message=message_mock)

        self.assertEqual(f"Η αναζήτηση για τον όρο 'Tsipras' τερματίστηκε", message_mock.method_calls[0].args[0])
        self.assertEqual(settings_helper.search_keyword, "")
        self.assertEqual(settings_helper.page_number, 1)

    @patch.object(settings_helper, 'search_keyword', '')
    async def test_end_search2(self):

        # english
        text_mock = "No 👎"
        message_mock = AsyncMock(text=text_mock)
        dict_for_message_mock = {"from": {"id": "1234"}}
        message_mock.__getitem__.side_effect = dict_for_message_mock.__getitem__
        settings_helper.settings["1234"] = {"lang": "English"}
        await end_search(message=message_mock)

        self.assertEqual(f"Search is ended", message_mock.method_calls[0].args[0])
        self.assertEqual(settings_helper.search_keyword, "")
        self.assertEqual(settings_helper.page_number, 1)

        # Greek
        text_mock = "Όχι 👎"
        message_mock = AsyncMock(text=text_mock)
        dict_for_message_mock = {"from": {"id": "1234"}}
        message_mock.__getitem__.side_effect = dict_for_message_mock.__getitem__
        settings_helper.settings["1234"] = {"lang": "Greek"}
        await end_search(message=message_mock)

        self.assertEqual(f"Η αναζήτηση τερματίστηκε", message_mock.method_calls[0].args[0])
        self.assertEqual(settings_helper.search_keyword, "")
        self.assertEqual(settings_helper.page_number, 1)

    async def test_search_category(self):

        url = convert_category_str_to_url(category_str='news')
        search_results = CategoryScraper(url=url, header=_header())
        dict_from_search_results = {}
        for _dataclass in search_results.news_list:
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

        text_mock = "/c news"
        message_mock = AsyncMock(text=text_mock)
        dict_for_message_mock = {"from": {"id": "1234"}}
        message_mock.__getitem__.side_effect = dict_for_message_mock.__getitem__
        settings_helper.settings["1234"] = {"lang": "English"}
        await search_category(message=message_mock)

        self.assertEqual(settings_helper.page_number, 2)

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
