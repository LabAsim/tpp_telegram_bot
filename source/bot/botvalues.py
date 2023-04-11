"""A module containing the Bot"""
import json
import logging
import os
import sys
from typing import Any, Union

from aiogram import Bot, Dispatcher, types, md
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from source.helper.helper import file_exists
from source.helper.search import SearchTerm
from source.bot.apify_actor import call_apify_actor, synthesize_url, convert_category_str_to_url


class BotConstructor:
    """Constructs the bot"""

    def __init__(self, telegram_token: str, apify_token: str, dispatcher, test: bool = False):

        self.page_number = 1
        self.search_results: Union[SearchTerm, dict] = Any
        self.search_keyword: str = ""
        self.telegram_token = telegram_token
        self.apify_token = apify_token
        self.proxy_url = "http://proxy.server:3128"
        self.proxies = {"http": self.proxy_url}
        proxy_url = "http://proxy.server:3128"
        # Create the bot
        '''if not test:
            # The proxy is needed only if the Bot is used on pythonanywhere.com
            bot = Bot(token=telegram_token, parse_mode=types.ParseMode.MARKDOWN_V2,
                      timeout=180, proxy=proxy_url)
        else:
            bot = Bot(token=telegram_token, parse_mode=types.ParseMode.MARKDOWN_V2,
                      timeout=180)
        global dp
        dp = Dispatcher(bot)'''
        self.dp = dispatcher
        self.dir_path_exe = self.find_the_path_of_main_exe()
        self.dir_path = self.find_the_path_of_main()
        # Load the saved settings
        self.settings: dict = self.read_settings_from_file()  # {user_id: {"lang": lang} }
        print(f"Settings: {self.settings}")

        # language selection
        lang1 = KeyboardButton('English 👍')
        lang2 = KeyboardButton('Greek 🤝')
        self.lang_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(lang1).add(lang2)

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
            self.search_results = call_apify_actor(actor="athletic_scraper/my-actor",
                                                   url=url, token=self.apify_token)["results_total"]
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

        @self.dp.message_handler(commands=['category', "Category", "c", "κατηγορία", "κατηγορια", "κ", ])
        async def search_category(message: types.Message):
            """
            Scrapes the provided news category athletic_scraper/category-actor
            """
            logging.info(f"{message.from_user.first_name}: {message.text}")
            # Reset the counter
            self.page_number = 1
            self.search_keyword = message.text.strip().replace("/category", "").strip()
            self.search_keyword = self.search_keyword.strip().replace("/c", "").strip()
            self.search_keyword = self.search_keyword.strip().replace("/κατηγορία", "").strip()
            self.search_keyword = self.search_keyword.strip().replace("/κατηγορια", "").strip()
            self.search_keyword = self.search_keyword.strip().replace("/κ", "").strip()

            url = convert_category_str_to_url(category_str=self.search_keyword)
            # Add 1 one to the counter
            self.page_number += 1
            self.search_results = call_apify_actor(actor="athletic_scraper/category-actor",
                                                   url=url, token=self.apify_token)["results_total"]
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

    def save_all_settings(self):
        """
        Saves all settings to `settings.json`.
        :return: None
        """
        dir_path = self.dir_path
        save_settings_to_dump = self.settings
        if file_exists(name="settings.json", dir_path=dir_path):
            json_data = ''
            with open(os.path.join(dir_path, "settings.json"), "r+", encoding='utf-8') as file:
                json_data = json.load(file)
                if len(json_data) == 0:  # To avoid empty string in the text file
                    json_data = save_settings_to_dump
                else:
                    json_data.update(save_settings_to_dump)
            with open(os.path.join(dir_path, "settings.json"), "w+", encoding='utf-8') as file:
                json.dump(json_data, file, indent=4)
                print(f"Settings saved in: {os.path.join(dir_path, 'settings.json')}"
                      f"\n Settings: {save_settings_to_dump}")
        else:  # Settings.json does not exist.
            with open(os.path.join(dir_path, "settings.json"), "w+", encoding='utf-8') as file:
                json_data = save_settings_to_dump
                json.dump(json_data, file, indent=4)
                print(f"Settings saved in: {os.path.join(dir_path, 'settings.json')}"
                      f"\n Settings: {save_settings_to_dump}")

    def overwrite_save_settings(self) -> None:
        """Overwrites current settings to settings.json"""
        dir_path = self.dir_path
        save_settings_to_dump = self.settings
        with open(os.path.join(dir_path, "settings.json"), "w+", encoding='utf-8') as file:
            json.dump(save_settings_to_dump, file, indent=4)
            print(f"Settings saved in: {os.path.join(dir_path, 'settings.json')}"
                  f"\n Settings: {save_settings_to_dump}")


    def read_settings_from_file(self) -> dict | None:
        """
        Reads the settings from `settings.json`.
        :return: A dictionary with the settings or None, if no json file exists.

        """

        if file_exists(name="settings.json", dir_path=self.dir_path):
            with open(os.path.join(self.dir_path, "settings.json"), "r+", encoding='utf-8') as file:
                json_data = json.load(file)
                if len(json_data) == 0:
                    return None  # To avoid empty string in the text file
                print(json_data)
                return json_data
        return {}

    def find_the_path_of_main_exe(self) -> str:
        """
        Returns The path of the directory of main.py or .exe
        :return: The path of the directory of main.py or .exe
        """
        if getattr(sys, 'frozen', False):
            print(getattr(sys, 'frozen', False))
            # The temporary path of the file when the app runs as an .exe
            self.dir_path_exe = os.path.dirname(os.path.realpath(sys.executable))
            # self.dir_path_exe = os.path.dirname(self.dir_path_exe)  # We need the parent of the parent of this directory
            # self.dir_path = os.path.dirname(self.dir_path)  # We need the parent of the parent of this directory
            # If the path until this step contains \\scrape_tpp_gui, get the parent dir, which is a temp dir(MEIPP).
            # self.dir_path = os.path.dirname(self.dir_path)
            print(f"{self}>Exe(self.dir_path_exe):", self.dir_path_exe)
            return self.dir_path_exe
        elif __file__:
            self.dir_path_exe = os.path.dirname(__file__)  # We need the parent of the parent of this directory
            self.dir_path_exe = os.path.dirname(self.dir_path_exe)  # We need the parent of the parent of this directory
            self.dir_path_exe = os.path.dirname(self.dir_path_exe)
            print(f'{self}>Script (self.dir_path_exe): {self.dir_path_exe}')
            return self.dir_path_exe

    def find_the_path_of_main(self) -> str:
        """
        Returns The path of the directory of main.py or the temporary folder hosting the files i.e.: `Temp/_MEI71042`
        if the app is running as an .exe
        :return: The path of the directory of main.py or the temporary folder
        """
        if getattr(sys, 'frozen', False):
            print(getattr(sys, 'frozen', False))
            # The temporary path of the file when the app runs as an .exe
            self.dir_path = os.path.dirname(os.path.realpath(__file__))
            self.dir_path = os.path.dirname(self.dir_path)  # We need the parent of the parent of this directory
            self.dir_path = os.path.dirname(self.dir_path)  # We need the parent of the parent of this directory
            print(f"{self}>Exe (self.dir_path):", self.dir_path)
            return self.dir_path
        elif __file__:
            self.dir_path = os.path.dirname(__file__)  # We need the parent of the parent of this directory
            self.dir_path = os.path.dirname(self.dir_path)  # We need the parent of the parent of this directory
            self.dir_path = os.path.dirname(self.dir_path)
            print(f'{self}>Script (self.dir_path): {self.dir_path}')
            return self.dir_path
