"""A module containing the Bot"""
import asyncio
import logging
import os
import shutil
import threading
import colorama
from typing import Coroutine
from aiogram import types, md, Dispatcher

import config
import saved_tokens
import source.db.funcs
from source.bot.apify_actor import (
    call_apify_actor,
    synthesize_url,
    convert_category_str_to_url,
)
from source.bot.bot_dispatcher import choose_token, botify
from source.bot.botvalues import BotHelper
from source.bot.commands_text import Text
from source.helper.youtube_funcs import download_playlist, download_send

logger = logging.getLogger(__name__)

token = choose_token(test=config.TEST)

# The dp needs to be instantiated here. Otherwise, the functions are not registered (don't know why though)
bot = botify(token=token, proxy_url=config.PROXY_URL_PYTHONANYWHERE, mode=config.MODE)
dp = Dispatcher(bot)  # , run_tasks_by_default=True

settings_helper = BotHelper(
    dispatcher=dp, apify_token=saved_tokens.TOKEN_APIFY, telegram_token=token
)


@dp.message_handler(lambda message: message.text in ("English 👍", "Greek 🤝"))
async def save_user(message: types.Message) -> None:
    """Saves the user's name and lang preference"""
    await save_language(message=message)
    await save_name(message=message)
    await source.db.funcs.connect(message=message)


async def save_language(message: types.Message) -> None:
    """Saves the language preference of the target user"""
    logger.info(message)
    user_id = message["from"]["id"]
    lang = message.text.strip("👍").strip("🤝").strip()
    try:
        settings_helper.settings[f"{user_id}"]["lang"] = lang
    except KeyError:
        settings_helper.settings[f"{user_id}"] = {}
        settings_helper.settings[f"{user_id}"]["lang"] = lang
    # print(f"{settings_helper.settings}")
    settings_helper.save_all_settings()
    markup = types.ReplyKeyboardRemove()
    if settings_helper.settings[f"{user_id}"]["lang"] == "English":
        await message.answer(Text.save_lang_text_eng, reply_markup=markup)
    else:
        await message.answer(Text.save_lang_text_greek, reply_markup=markup)
    await show_help(message=message)


async def save_name(message: types.Message) -> None:
    """Saves the language preference of the target user"""
    # print(message)
    user_id = message["from"]["id"]
    first_name = message["from"]["first_name"]
    try:
        settings_helper.settings[f"{user_id}"]["first_name"] = first_name
    except KeyError:
        settings_helper.settings[f"{user_id}"] = {}
        settings_helper.settings[f"{user_id}"]["first_name"] = first_name
    logger.info(f"{settings_helper.settings}")
    settings_helper.save_all_settings()


@dp.message_handler(commands=["lang", "language", "start"])
async def choose_language(message: types.message) -> Coroutine:
    """Choose and saves the language preference of the user"""

    return await message.answer(Text.choose_lang_text, reply_markup=settings_helper.lang_kb)


@dp.message_handler(commands=["help"])
async def show_help(message: types.Message):
    """Shows the help message"""
    user_id = message["from"]["id"]
    if str(user_id) in list(settings_helper.settings.keys()):
        if settings_helper.settings[f"{user_id}"]["lang"] == "English":
            answer = Text.help_text_eng
        else:
            answer = Text.help_text_greek
        await message.answer(answer)
    else:
        # while str(user_id) not in list(settings_helper.settings.keys()):
        # asyncio.get_event_loop()
        # new_loop = asyncio.new_event_loop()
        # loop.run_until_complete(asyncio.gather(choose_language(message=message)))

        # task = asyncio.create_task(choose_language(message=message))

        # r =  asyncio.gather(choose_language(message=message))
        # logging.info(f"\n\n\n\t\t\t\t {r}  {type(r)}")
        # await asyncio.wait(r)
        # done, pending = await asyncio.wait(r)

        # await asyncio.sleep(1)
        await choose_language(message=message)
        if str(user_id) in list(settings_helper.settings.keys()):
            await show_help(message=message)


async def search(message: types.Message):
    """Searches based on the user's input and replies with the search results"""
    logger.info(f"{message.from_user.first_name}: {message.text}\n\n\n\n")
    # Reset the counter
    settings_helper.page_number = 1
    settings_helper.search_keyword = message.text.strip().replace("/search", "").strip()
    settings_helper.search_keyword = (
        settings_helper.search_keyword.strip().replace("/s", "").strip()
    )
    settings_helper.search_keyword = (
        settings_helper.search_keyword.strip().replace("/σ", "").strip()
    )
    url = synthesize_url(keyword=settings_helper.search_keyword, page_number=1)
    # Add 1 one to the counter
    settings_helper.page_number += 1
    # settings_helper.search_results = call_apify_actor(
    #     actor="athletic_scraper/my-actor", url=url, token=settings_helper.apify_token
    # )["results_total"]
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(
        None, call_apify_actor, "athletic_scraper/my-actor", url, settings_helper.apify_token
    )
    settings_helper.search_results = results["results_total"]
    answer = md.text()
    for result_dict_key in list(settings_helper.search_results.keys()):
        title = result_dict_key
        url = settings_helper.search_results[result_dict_key]
        last_line = "-" * 50
        answer += md.text(
            md.text(""),
            md.bold((md.text(title))),
            md.text(md.escape_md(url)),
            md.text(md.escape_md(last_line)),
            sep="\n",
        )

    markup = types.ReplyKeyboardRemove()

    await message.reply(
        answer,
        reply_markup=markup,
        disable_web_page_preview=True,
        parse_mode=types.ParseMode.MARKDOWN_V2,
    )


@dp.message_handler(commands=["search", "s", "σ"])
async def search_handler(message: types.Message):
    """Searches based on the user's input, replies with the search results and waits the user to interact"""
    await search(message=message)
    await to_search_next_page(message=message)


@dp.message_handler(lambda message: "arbitrary text, it does not mean anything" == message.text)
async def to_search_next_page(message: types.Message) -> None:
    """
    Asks the user whether to search the next page
    """
    # Configure ReplyKeyboardMarkup
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    user_id = message["from"]["id"]
    if str(user_id) in list(settings_helper.settings.keys()):
        if settings_helper.settings[f"{user_id}"]["lang"] == "English":
            markup.add("Yes 🆗", "No 👎")
            await message.reply(Text.to_search_next_page_eng, reply_markup=markup)
        else:
            markup.add("Ναι 🆗", "Όχι 👎")
            await message.reply(Text.to_search_next_page_greek, reply_markup=markup)
    else:
        await choose_language(message=message)
        # await asyncio.sleep(6)
        if str(user_id) in list(settings_helper.settings.keys()):
            await to_search_next_page(message=message)


@dp.message_handler(lambda message: "Yes 🆗" == message.text)
@dp.message_handler(lambda message: "Ναι 🆗" == message.text)
async def search_next_page(message: types.Message) -> None:
    """Searches the next page"""
    user_id = message["from"]["id"]
    # Check if the keyword is empty and the page number is 1.
    # If True, then prompt to search something first and stop the function.
    if settings_helper.search_keyword == "" and settings_helper.page_number == 1:
        markup = types.ReplyKeyboardRemove()
        if settings_helper.settings[f"{user_id}"]["lang"] == "English":
            await message.answer(
                text=Text.search_next_page_empty_keyword_page_no_1_eng,
                reply_markup=markup,
            )
        else:
            await message.answer(
                text=Text.search_next_page_empty_keyword_page_no_1_greek,
                reply_markup=markup,
            )
        return None
    url = synthesize_url(
        keyword=settings_helper.search_keyword, page_number=settings_helper.page_number
    )
    # Add 1 to the counter
    settings_helper.page_number += 1

    # This is a non-async way, which blocks main loop.

    # settings_helper.search_results = call_apify_actor(
    #     url=url, token=settings_helper.apify_token, actor="athletic_scraper/my-actor"
    # )["results_total"]

    # Fetch the results
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(
        None, call_apify_actor, "athletic_scraper/my-actor", url, settings_helper.apify_token
    )
    settings_helper.search_results = results["results_total"]
    answer = ""
    for result_dict_key in list(settings_helper.search_results.keys()):
        title = result_dict_key
        url = settings_helper.search_results[result_dict_key]
        last_line = "-" * 50
        answer += md.text(
            md.text(""),
            md.bold(md.text(title)),
            md.text(md.escape_md(url)),
            md.text(md.escape_md(last_line)),
            sep="\n",
        )

    # Remove the Keyboard
    markup = types.ReplyKeyboardRemove()

    # If there is not any scraped data from the next page, the answer is empty and an exception will be raised.
    reply_to_empty_results = ""
    if answer == "":
        reply_to_empty_results = (
            f"There are not any more results for the keyword: {settings_helper.search_keyword}"
        )
        answer = reply_to_empty_results

    # Reply to the user
    await message.answer(f"{md.text(answer)}", reply_markup=markup)

    # Prompt to search the next page only if the current search was successful.
    if answer != reply_to_empty_results:
        await to_search_next_page(message=message)


@dp.message_handler(lambda message: "No 👎" == message.text)
@dp.message_handler(lambda message: "Όχι 👎" == message.text)
async def end_search(message: types.Message):
    """
    Removes the keyboard and inform the user that the search was ended.
    """
    user_id = message["from"]["id"]
    markup = types.ReplyKeyboardRemove()
    if settings_helper.search_keyword != "":
        if settings_helper.settings[f"{user_id}"]["lang"] == "English":
            await message.answer(
                f"Search for '{settings_helper.search_keyword}' is ended",
                reply_markup=markup,
            )
        else:
            await message.answer(
                f"Η αναζήτηση για τον όρο '{settings_helper.search_keyword}' τερματίστηκε",
                reply_markup=markup,
            )
    else:
        if settings_helper.settings[f"{user_id}"]["lang"] == "English":
            await message.answer("Search is ended", reply_markup=markup)
        else:
            await message.answer("Η αναζήτηση τερματίστηκε", reply_markup=markup)
    # Delete the keyword.
    settings_helper.search_keyword = ""
    # Reset the page number
    settings_helper.page_number = 1


@dp.message_handler(
    commands=[
        "category",
        "Category",
        "c",
        "κατηγορία",
        "κατηγορια",
        "κ",
    ]
)
async def search_category(message: types.Message):
    """
    Scrapes the provided news category athletic_scraper/category-actor
    """
    logger.info(f"{message.from_user.first_name}: {message.text}")
    # Reset the counter
    settings_helper.page_number = 1
    settings_helper.search_keyword = message.text.strip().replace("/category", "").strip()
    settings_helper.search_keyword = (
        settings_helper.search_keyword.strip().replace("/c", "").strip()
    )
    settings_helper.search_keyword = (
        settings_helper.search_keyword.strip().replace("/κατηγορία", "").strip()
    )
    settings_helper.search_keyword = (
        settings_helper.search_keyword.strip().replace("/κατηγορια", "").strip()
    )
    settings_helper.search_keyword = (
        settings_helper.search_keyword.strip().replace("/κ", "").strip()
    )

    url = convert_category_str_to_url(category_str=settings_helper.search_keyword)
    # If the url does not exist (it's empty string), stop the method
    if url == "":
        return None
    # Add 1 one to the counter
    settings_helper.page_number += 1
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(
        None, call_apify_actor, "athletic_scraper/category-actor", url, settings_helper.apify_token
    )
    settings_helper.search_results = results["results_total"]

    # That is a sync way, which blocks main loop

    # settings_helper.search_results = call_apify_actor(
    #     actor="athletic_scraper/category-actor",
    #     url=url,
    #     token=settings_helper.apify_token,
    # )["results_total"]

    answer = md.text()
    for result_dict_key in list(settings_helper.search_results.keys()):
        title = result_dict_key
        url = settings_helper.search_results[result_dict_key]
        last_line = "-" * 50
        answer += md.text(
            md.text(""),
            md.bold((md.text(title))),
            md.text(md.escape_md(url)),
            md.text(md.escape_md(last_line)),
            sep="\n",
        )
    # logging.debug(f"Answer forwarded to user:{answer}")
    markup = types.ReplyKeyboardRemove()
    # Reply to user
    await message.reply(
        answer,
        reply_markup=markup,
        disable_web_page_preview=True,
        parse_mode=types.ParseMode.MARKDOWN_V2,
    )


# @dp.message_handler(lambda message: message)
async def check_user(message: types.Message):
    user_id = message["from"]["id"]

    async def loop_check(message: types.Message):
        # while True:
        if str(user_id) not in list(settings_helper.settings.keys()):
            await choose_language(message=message)
        else:
            await asyncio.sleep(10)

    task = asyncio.create_task(loop_check(message))
    await task


@dp.message_handler(commands=["youtube", "video", "yt"])
async def send_video(message: types.Message) -> None:
    """Downloads and sends the video(s) from the url provided by the user"""

    if "playlist" in message.text:
        playlist_folder = await download_playlist(message.text)
        count_files = len(os.listdir(playlist_folder))
        for video in os.listdir(playlist_folder):
            video_path = os.path.join(playlist_folder, video)
            input_file = types.InputFile(video_path)
            await message.answer_document(document=input_file)
        else:
            await asyncio.sleep(3 * count_files)
            thr = threading.Thread(target=lambda: shutil.rmtree(playlist_folder))
            thr.start()
            logger.debug(
                f"{colorama.Fore.GREEN}'Folder: {playlist_folder} removed'{colorama.Style.RESET_ALL}"
            )
            return None

    downloaded_file = None

    try:
        downloaded_file = await download_send(message=message)
        await message.answer_document(document=downloaded_file)
    except Exception as err:
        logger.warning(err)
    finally:
        thr = threading.Thread(target=lambda: os.remove(downloaded_file.file.name))
        thr.start()
        logger.debug(
            f"{colorama.Fore.GREEN}{downloaded_file.file.name} deleted{colorama.Style.RESET_ALL}"
        )
