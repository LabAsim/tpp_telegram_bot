"""A module containing the Bot"""
import json
import os
import sys
from typing import Any, Union
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from source.helper.helper import file_exists
from source.helper.search import SearchTerm


class BotConstructor:
    """Constructs the bot"""

    def __init__(self, telegram_token: str, apify_token: str, dispatcher, debug):

        self.page_number = 1
        self.search_results: Union[SearchTerm, dict] = Any
        self.search_keyword: str = ""
        self.telegram_token = telegram_token
        self.apify_token = apify_token
        self.DEBUG = debug
        self.proxy_url = "http://proxy.server:3128"
        self.proxies = {"http": self.proxy_url}
        self.dp = dispatcher
        self.dir_path_exe = self.find_the_path_of_main_exe()
        self.dir_path = self.find_the_path_of_main()
        # Load the saved settings
        self.settings: dict = self.read_settings_from_file()  # {user_id: {"lang": lang} }
        if self.DEBUG:
            print(f"Settings: {self.settings}")

        # language selection
        lang1 = KeyboardButton('English 👍')
        lang2 = KeyboardButton('Greek 🤝')
        self.lang_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(lang1).add(lang2)

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
                    #return None  # To avoid empty string in the text file
                    return {}
                if self.DEBUG:
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
            if self.DEBUG:
                print(f"{self}>Exe(self.dir_path_exe):", self.dir_path_exe)
            return self.dir_path_exe
        elif __file__:
            self.dir_path_exe = os.path.dirname(__file__)  # We need the parent of the parent of this directory
            self.dir_path_exe = os.path.dirname(self.dir_path_exe)  # We need the parent of the parent of this directory
            self.dir_path_exe = os.path.dirname(self.dir_path_exe)
            if self.DEBUG:
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
