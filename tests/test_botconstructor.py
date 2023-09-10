import json
import os
import unittest

from aiogram import Dispatcher

from source.bot.bot_dispatcher import botify, choose_token
from source.bot.botvalues import BotHelper
from config import PROXY_URL_PYTHONANYWHERE
from source.helper.helper import file_exists


class TestBotConstructor(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        bot = botify(token=choose_token(), proxy_url=PROXY_URL_PYTHONANYWHERE, mode="self")
        dp = Dispatcher(bot)
        self._bot = BotHelper(telegram_token="", apify_token="", dispatcher=dp)

    def test_save_all_settings(self):
        """
        1) Check that the function appends the new settings to the json file

        2) Check that the function overwrites the json file if it is empty

        3) Delete the file if the file exists, create a new one and save the settings. Then check that it does
         exist.

        :return: None
        """

        original_settings_json = {}
        with open(
            os.path.join(self._bot.dir_path, "settings.json"), "r+", encoding="utf-8"
        ) as file:
            original_settings_json = json.load(file)
        settings_to_dump = {"234": {"lang": "English"}}
        self._bot.settings.update(settings_to_dump)
        self._bot.save_all_settings()

        # 1
        with open(
            os.path.join(self._bot.dir_path, "settings.json"), "r+", encoding="utf-8"
        ) as file:
            json_data = json.load(file)
            self.assertEqual(self._bot.settings, json_data)

        del self._bot.settings["234"]

        with open(
            os.path.join(self._bot.dir_path, "settings.json"), "w+", encoding="utf-8"
        ) as file:
            json.dump(self._bot.settings, file, indent=4)

        # 2
        empty_dict = {}
        with open(
            os.path.join(self._bot.dir_path, "settings.json"), "w+", encoding="utf-8"
        ) as file:
            json.dump(empty_dict, file, indent=4)
        with open(
            os.path.join(self._bot.dir_path, "settings.json"), "r+", encoding="utf-8"
        ) as file:
            json_data = json.load(file)
            self.assertEqual(json_data, empty_dict)
        with open(
            os.path.join(self._bot.dir_path, "settings.json"), "w+", encoding="utf-8"
        ) as file:
            json.dump(self._bot.settings, file, indent=4)

        # 3
        if file_exists(name="settings.json", dir_path=self._bot.dir_path):
            os.remove(os.path.join(self._bot.dir_path, "settings.json"))
        self._bot.overwrite_save_settings()
        with open(
            os.path.join(self._bot.dir_path, "settings.json"), "r+", encoding="utf-8"
        ) as file:
            json_data = json.load(file)
            self.assertEqual(self._bot.settings, json_data)

        # Rewrite the original settings
        with open(
            os.path.join(self._bot.dir_path, "settings.json"), "w+", encoding="utf-8"
        ) as file:
            json.dump(original_settings_json, file, indent=4)

    def test_overwrite_save_settings(self):
        """
        Read the saved settings, overwrite the file,
        check that the file is indeed overwritten and rewrite the previous settings.
        :return: None
        """
        original_settings = self._bot.settings
        settings_to_dump = {"234": {"lang": "English"}}
        self._bot.settings = settings_to_dump
        self._bot.save_all_settings()
        with open(
            os.path.join(self._bot.dir_path, "settings.json"), "w+", encoding="utf-8"
        ) as file:
            json.dump(settings_to_dump, file, indent=4)
        with open(
            os.path.join(self._bot.dir_path, "settings.json"), "r+", encoding="utf-8"
        ) as file:
            json_data = json.load(file)
            self.assertEqual(json_data, settings_to_dump)
        with open(
            os.path.join(self._bot.dir_path, "settings.json"), "w+", encoding="utf-8"
        ) as file:
            json.dump(original_settings, file, indent=4)

    def test_read_settings_from_file(self):
        """
        If file exists
            1) empty the file and check that None is returned
            2) Overwrite with arbitrary data and check that this arbitrary data is returned as a dict

        If file does not exist, return an empty dict
        :return: None
        """
        pass
