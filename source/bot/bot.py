import asyncio
import logging
from typing import Any, Union
import requests
from aiogram import Bot, Dispatcher, executor, types, md
from aiogram.dispatcher.filters.state import StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton  # for reply keyboard (sends message)
from source.helper.search import SearchTerm
from source.bot.apify_actor import call_apify_actor, synthesize_url


class BotConstructor:
    """Constructs the bot"""

    def __init__(self, telegram_token: str, apify_token: str, test: bool = False):
        self.page_number = 1
        self.search_results: Union[SearchTerm, dict] = Any
        self.search_keyword: str = ""
        self.telegram_token = telegram_token
        self.apify_token = apify_token
        # Create the bot
        self.proxy_url = "http://proxy.server:3128"
        self.proxies = {"http": self.proxy_url}
        if test:
            # The proxy is needed only if the Bot is used on pythonanywhere.com
            self.bot = Bot(token=self.telegram_token, parse_mode=types.ParseMode.MARKDOWN_V2,
                           timeout=180, proxy=self.proxy_url)
        else:
            self.bot = Bot(token=self.telegram_token, parse_mode=types.ParseMode.MARKDOWN_V2,
                           timeout=180)
        self.dp = Dispatcher(self.bot)
        # Create the commands
        self.create_start()
        self.create_help()
        self.create_search_cmd()
        print("Bot started!")

    def create_start(self):
        """Creates the interaction for the /start command"""
        answers = []  # store the answers they have given

        # language selection
        lang1 = KeyboardButton('English 👍')
        lang2 = KeyboardButton('Greek 🤝')
        lang_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(lang1).add(lang2)

        # sends welcome message after start
        @self.dp.message_handler(commands=['start'])
        async def welcome(message: types.Message):
            """

            :param message: The input command
            """
            await message.answer(
                md.escape_md('To search the TPP site, type /search <text> (or /s, /σ). Example: /search ΒΙΟΜΕ'))
            # await input.answer('Hello! Please select your language.'
            #                   '\nΓεια! Διάλεξε τι γλώσσα επιλογής σου',
            #                   reply_markup=lang_kb)

    def create_help(self):
        """
        A help message
        """

        @self.dp.message_handler(commands=['help'])
        async def help(message: types.Message):
            await message.answer(
                md.escape_md('To search the TPP site, type /search <text>. Example: /search ΒΙΟΜΕ'))

    def create_search_cmd(self):
        """Creates the search command interface and logic"""

        @self.dp.message_handler(commands=['search', 's', 'σ'])
        async def respond(message: types.Message):
            """Searches based on the user's input and replies with the search results"""
            logging.info(f"{message.from_user.first_name}: {message.text}")
            # Reset the counter
            self.page_number = 1
            self.search_keyword = message.text.strip().replace("/search", "").strip()
            self.search_keyword = self.search_keyword.strip().replace("/s", "").strip()
            self.search_keyword = self.search_keyword.strip().replace("/σ", "").strip()
            url = synthesize_url(keyword=self.search_keyword, page_number=1)
            # Add 1 one to the counter
            self.page_number += 1
            self.search_results = call_apify_actor(url=url, token=self.apify_token)["results_total"]
            answer = md.text()
            for result_dict_key in list(self.search_results.keys()):
                title = result_dict_key
                url = self.search_results[result_dict_key]
                last_line = ("-" * 50)
                answer += md.text(
                    md.text(""),
                    md.bold((md.text(title))),
                    md.text(md.escape_md(url)),
                    md.text(md.escape_md(last_line)), sep="\n")
            # print(f"{answer}")
            markup = types.ReplyKeyboardRemove()
            # Reply to user
            await message.reply(answer, reply_markup=markup, disable_web_page_preview=True,
                                parse_mode=types.ParseMode.MARKDOWN_V2)
            # Wait the for user's input
            await to_search_next_page(message=message)

        @self.dp.message_handler(lambda message: "search" in message.text)
        async def to_search_next_page(message: types.Message) -> None:
            """
            Asks the user whether to search the next page
            """

            # Configure ReplyKeyboardMarkup
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add("Yes", "No")

            await message.reply("Do you want to search the next page?", reply_markup=markup)

        @self.dp.message_handler(lambda message: "Yes" in message.text)
        async def search_next_page(message: types.Message) -> None:
            """Searches the next page"""

            # Check if the keyword is empty and the page number is 1.
            # If True, then prompt to search something first and stop the function.
            if self.search_keyword == "" and self.page_number == 1:
                markup = types.ReplyKeyboardRemove()
                await message.answer(text=md.escape_md("Nothing to search."
                                                       "\nRepeat the search command /search <keyword>"),
                                     reply_markup=markup)
                return None
            url = synthesize_url(keyword=self.search_keyword, page_number=self.page_number)
            # Add 1 to the counter
            self.page_number += 1
            # Fetch the results
            self.search_results = call_apify_actor(url=url, token=self.apify_token)["results_total"]
            answer = ""
            for result_dict_key in list(self.search_results.keys()):
                title = result_dict_key
                url = self.search_results[result_dict_key]
                last_line = ("-" * 50)
                answer += md.text(
                    md.text(""),
                    md.bold(md.text(title)),
                    md.text(md.escape_md(url)),
                    md.text(md.escape_md(last_line)), sep="\n")

            # Remove the Keyboard
            markup = types.ReplyKeyboardRemove()

            # If there is not any scraped data from the next page, the answer is empty and an exception will be raised.
            reply_to_empty_results = ""
            if answer == "":
                reply_to_empty_results = f"There are not any more results for the keyword: {self.search_keyword}"
                answer = reply_to_empty_results

            # Reply to the user
            await message.answer(f"{md.text(answer)}", reply_markup=markup)

            # Prompt to search the next page only if the current search was successful.
            if answer != reply_to_empty_results:
                await to_search_next_page(message=message)

        @self.dp.message_handler(lambda message: "No" in message.text)
        async def end_search(message: types.Message):
            """
            Removes the keyboard and inform the user that the search was ended.
            """
            markup = types.ReplyKeyboardRemove()
            if self.search_keyword != "":
                await message.answer(f"Search for '{self.search_keyword}' is ended", reply_markup=markup)
            else:
                await message.answer(f"Search is ended", reply_markup=markup)
            # Delete the keyword.
            self.search_keyword = ""
            # Reset the page number
            self.page_number = 1
