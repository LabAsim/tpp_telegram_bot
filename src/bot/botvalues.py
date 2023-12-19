"""A module containing the Bot"""
import os
import sys
from typing import Union, Any

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from apify_actor.main import SearchTerm
import logging

logger = logging.getLogger(__name__)


class BotHelper:
    """Configures the settings"""

    def __init__(self, telegram_token: str, apify_token: str, dispatcher):
        self.page_number = 1
        self.search_results: Union[SearchTerm, dict] = Any
        self.search_keyword: str = ""
        self.telegram_token = telegram_token
        self.apify_token = apify_token
        self.proxy_url = "http://proxy.server:3128"
        self.proxies = {"http": self.proxy_url}
        self.dp = dispatcher
        # language selection
        lang1 = KeyboardButton("English 👍")
        lang2 = KeyboardButton("Greek 🤝")
        self.lang_kb = (
            ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(lang1).add(lang2)
        )
        self.dir_path_exe = self.find_the_path_of_main_exe()
        self.dir_path = self.find_the_path_of_main()
        # Load the saved settings
        # self.settings: dict = self.read_settings_from_file()  # {user_id: {"lang": lang} }

    def find_the_path_of_main_exe(self) -> str:
        """
        Returns The path of the directory of main.py or .exe
        :return: The path of the directory of main.py or .exe
        """
        if getattr(sys, "frozen", False):
            logger.debug(getattr(sys, "frozen", False))
            # The temporary path of the file when the app runs as an .exe
            self.dir_path_exe = os.path.dirname(os.path.realpath(sys.executable))

            logger.debug(f"{self}>Exe(self.dir_path_exe):", self.dir_path_exe)
            return self.dir_path_exe
        elif __file__:
            self.dir_path_exe = os.path.dirname(
                __file__
            )  # We need the parent of the parent of this directory
            self.dir_path_exe = os.path.dirname(
                self.dir_path_exe
            )  # We need the parent of the parent of this directory
            self.dir_path_exe = os.path.dirname(self.dir_path_exe)
            logger.debug(f"{self}>Script (self.dir_path_exe): {self.dir_path_exe}")
            return self.dir_path_exe

    def find_the_path_of_main(self) -> str:
        """
        Returns The path of the directory of main.py or
        the temporary folder hosting the files i.e.: `Temp/_MEI71042`
        if the app is running as an .exe
        :return: The path of the directory of main.py or the temporary folder
        """
        if getattr(sys, "frozen", False):
            logger.debug(getattr(sys, "frozen", False))
            # The temporary path of the file when the app runs as an .exe
            self.dir_path = os.path.dirname(os.path.realpath(__file__))
            self.dir_path = os.path.dirname(
                self.dir_path
            )  # We need the parent of the parent of this directory
            self.dir_path = os.path.dirname(
                self.dir_path
            )  # We need the parent of the parent of this directory
            logger.debug(f"{self}>Exe (self.dir_path):", self.dir_path)
            return self.dir_path
        elif __file__:
            self.dir_path = os.path.dirname(
                __file__
            )  # We need the parent of the parent of this directory
            self.dir_path = os.path.dirname(
                self.dir_path
            )  # We need the parent of the parent of this directory
            self.dir_path = os.path.dirname(self.dir_path)
            logger.debug(f"{self}>Script (self.dir_path): {self.dir_path}")
            return self.dir_path
