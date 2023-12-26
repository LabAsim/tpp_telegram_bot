"""A module containing the Bot"""
import asyncio
import inspect
import os
import shutil
import threading
from datetime import datetime, timezone
from functools import wraps
import logging
from typing import Coroutine, AsyncIterable, Callable, Any
from aiogram import types, md, Dispatcher, utils
from itertools import islice

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from asyncpg import NotNullViolationError

import config
import src.db.funcs
from src.bot.apify_actor import (
    call_apify_actor,
    synthesize_url,
    convert_category_str_to_url,
)
from src.db.funcs import fetch_schedule, delete_target_schedule
from src.bot.bot_dispatcher import choose_token, botify
from src.bot.botvalues import BotHelper
from src.bot.commands_text import Text
from src.helper.constants import rss_feed
from src.helper.rss_funcs import fetch_news, parse_commands_for_rssfeed
from src.helper.youtube_funcs import download_playlist, download_send
from src.helper.helper import log_func_name, func_name
from src.scheduler.funcs import schedule_rss_feed, get_my_schedules

try:
    import saved_tokens
except ModuleNotFoundError:
    from src.helper.helper import EnvVars as saved_tokens

logger = logging.getLogger(__name__)

token = choose_token(test=config.TEST)

# The dp needs to be instantiated here.
# Otherwise, the functions are not registered (don't know why though)
bot = botify(token=token, proxy_url=config.PROXY_URL_PYTHONANYWHERE, mode=config.MODE)
dp = Dispatcher(bot)  # , run_tasks_by_default=True

settings_helper = BotHelper(
    dispatcher=dp, apify_token=saved_tokens.TOKEN_APIFY, telegram_token=token
)


def update_user(func: Callable) -> Callable[[tuple[Any, ...]], Coroutine[Any, Any, Any]]:
    """
    A decorator to save the last_seen date,  in the db
    Modified from here: https://stackoverflow.com/a/14412901
    """

    @wraps(func)
    async def wrapper(*args, **kwargs) -> Coroutine:
        """The inner wrapper function"""
        try:
            if len(args) == 1 and len(kwargs) == 0:
                # Actual decorated function
                logger.debug("Plain decorator")
                # logger.debug(f"{args=}")
                # logger.debug(f'{kwargs.get("message")=}')
                # logger.info(type(args[0]))
                await src.db.funcs.update_user_info(message=args[0])
                return await func(*args)
            else:
                # Decorator with arguments
                logger.debug("Decorator called with arguments")
                # logger.debug(f"{args=}\n{kwargs=}")
                await src.db.funcs.update_user_info(message=kwargs.get("message"))
                return await func(*args, **kwargs)

        except (Exception, NotNullViolationError, RuntimeWarning, IndexError) as err:
            logger.exception(f"{err=}")

    return wrapper


@dp.message_handler(commands=["help", "χελπ", "ηελπ"])
@update_user
async def show_help(message: types.Message) -> None:
    """Shows the help message"""
    lang = await src.db.funcs.fetch_lang(message=message)
    lang = lang.get("lang")
    if lang == "English":
        answer = Text.help_text_eng
        answer2 = Text.help_text_eng2
        answer3 = Text.help_text_eng3
    else:
        answer = Text.help_text_greek
        answer2 = Text.help_text_greek2
        answer3 = Text.help_text_greek3
    await message.answer(answer)
    await message.answer(answer2)
    await message.answer(answer3)


@dp.message_handler(lambda message: message.text in ("English 👍", "Greek 🤝"))
@update_user
async def save_user(message: types.Message) -> None:
    """Saves the user's name and lang preference"""

    await src.db.funcs.connect(message=message)
    await show_help(message=message)


@dp.message_handler(commands=["lang", "language", "start", "λανγ"])
@update_user
async def choose_language(message: types.message) -> None:
    """Choose and saves the language preference of the user"""

    await message.answer(Text.choose_lang_text, reply_markup=settings_helper.lang_kb)


async def search(message: types.Message) -> None:
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
@update_user
async def search_handler(message: types.Message) -> None:
    """
    Searches based on the user's input,
    replies with the search results and waits the user to interact"""
    await search(message=message)
    logger.debug(f"{message=}")
    await to_search_next_page(message=message)
    logger.debug("ended..")


@dp.message_handler(lambda message: "arbitrary text, it does not mean anything" == message.text)
async def to_search_next_page(message: types.Message) -> None:
    """
    Asks the user whether to search the next page
    """
    # Configure ReplyKeyboardMarkup
    logger.info("to_search_next_page called")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    lang = await src.db.funcs.fetch_lang(message=message)
    logger.info(f"{lang=}")
    if lang == "English":
        markup.add("Yes 🆗", "No 👎")
        await message.reply(Text.to_search_next_page_eng, reply_markup=markup)
    else:
        markup.add("Ναι 🆗", "Όχι 👎")
        await message.reply(Text.to_search_next_page_greek, reply_markup=markup)


@dp.message_handler(lambda message: "Yes 🆗" == message.text)
@dp.message_handler(lambda message: "Ναι 🆗" == message.text)
@update_user
async def search_next_page(message: types.Message) -> None:
    """Searches the next page"""

    lang = await src.db.funcs.fetch_lang(message=message)
    # Check if the keyword is empty and the page number is 1.
    # If True, then prompt to search something first and stop the function.
    if settings_helper.search_keyword == "" and settings_helper.page_number == 1:
        markup = types.ReplyKeyboardRemove()
        if lang == "English":
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

    # If there is not any scraped data from the next page,
    # the answer is empty and an exception will be raised.
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
@update_user
async def end_search(message: types.Message):
    """
    Removes the keyboard and inform the user that the search was ended.
    """
    markup = types.ReplyKeyboardRemove()
    lang = await src.db.funcs.fetch_lang(message=message)
    if settings_helper.search_keyword != "":
        if lang == "English":
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
        if lang == "English":
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
@update_user
async def search_category(message: types.Message) -> None:
    """
    Scrapes the provided news category athletic_scraper/category-actor
    """
    log_func_name(thelogger=logger, fun_name=func_name(inspect.currentframe()))
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

    # Update the counter
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


@dp.message_handler(commands=["youtube", "video", "yt"])
@update_user
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
            logger.debug(f"'Folder: {playlist_folder} removed'")
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
        logger.debug(f"{downloaded_file.file.name} deleted")


@dp.message_handler(commands=rss_feed)
@update_user
async def send_rssfeed(
    message: types.Message = None, target_rss: str = None, chat_id: int = None
) -> None:
    """Sends the fetched news from the rss feed"""
    # logger.info(f"{message.text}")
    assert (message and target_rss) is None
    if not message:
        assert (target_rss and chat_id) is not None

    target = target_rss if not message else message.text.strip("/")
    target = await parse_commands_for_rssfeed(target)
    results = await fetch_news(target=target)
    # logger.debug(f"{results=}")
    answer = md.text()
    for entry in results:
        title = entry.title
        url = entry.link
        last_line = "-" * 50
        answer += md.text(
            md.text(""),
            md.bold((md.text(title))),
            md.text(md.escape_md(url)),
            md.text(md.escape_md(last_line)),
            sep="\n",
        )

    markup = types.ReplyKeyboardRemove()

    try:
        if message:
            await message.reply(
                answer,
                reply_markup=markup,
                disable_web_page_preview=True,
                parse_mode=types.ParseMode.MARKDOWN_V2,
            )
        else:
            await bot.send_message(
                chat_id=chat_id,
                text=answer,
                disable_web_page_preview=True,
                parse_mode=types.ParseMode.MARKDOWN_V2,
                reply_markup=markup,
            )
    except (utils.exceptions.MessageIsTooLong, utils.exceptions.BadRequest, Exception) as err:
        logger.warning(
            f"{len(results)=} {len(answer)=}"
            f"\n{err=}"
            f"\nAttempting to send chunks of the rss feed"
        )
        await send_chunks_rssfeed(
            results=results,
            message=message,
            chat_id=chat_id,
        )


async def send_chunks_rssfeed(
    results: list, message: types.Message, size: int = 10, chat_id: int = None
) -> None:
    """Sends chunks of the rssfeed"""

    async def chunks(data: list, size: int) -> AsyncIterable[list]:
        """https://stackoverflow.com/a/66555740"""
        it = iter(data)
        for i in range(0, len(data), size):
            yield [k for k in islice(it, size)]

    async for item in chunks(data=results, size=size):
        answer = md.text()
        for entry in item:
            title = entry.title
            url = entry.link
            last_line = "-" * 50
            answer += md.text(
                md.text(""),
                md.bold((md.text(title))),
                md.text(md.escape_md(url)),
                md.text(md.escape_md(last_line)),
                sep="\n",
            )
        markup = types.ReplyKeyboardRemove()
        if message:
            await message.reply(
                answer,
                reply_markup=markup,
                disable_web_page_preview=True,
                parse_mode=types.ParseMode.MARKDOWN_V2,
            )
        else:
            await bot.send_message(
                chat_id=chat_id,
                text=answer,
                disable_web_page_preview=True,
                parse_mode=types.ParseMode.MARKDOWN_V2,
                reply_markup=markup,
            )


@dp.message_handler(commands=["schedule", "sch"])
@update_user
async def schedule(message: types.Message):
    """Saves the schedule for the target rss site"""
    log_func_name(thelogger=logger, fun_name=func_name(inspect.currentframe()))
    logger.info(f"{message.text=}")
    chat_id = message["from"]["id"]
    logger.info(f"{message=}")
    # target_rss = message.text.strip("/").replace("schedule", "").replace("sch", "").strip()
    # Example: "/sch ert 1"
    message_split = message.text.split(" ")
    target_rss = message_split[1]
    logger.info(f"{target_rss=}")
    target_rss = await parse_commands_for_rssfeed(target_rss)
    trigger = None
    try:
        # Default 1 day
        day = int(message_split[2] if len(message_split) > 2 else 1)
        trigger = IntervalTrigger(
            days=day,
            start_time=datetime.now(timezone.utc),
        )
    except ValueError:
        trigger = CronTrigger(day_of_week=message_split[2])
    await schedule_rss_feed(chat_id=chat_id, target_rss=target_rss, trigger_target=trigger)


@dp.message_handler(commands=["mysch", "myschedule", "μυσψη"])
@update_user
async def my_schedule(message: types.Message) -> None:
    log_func_name(thelogger=logger, fun_name=func_name(inspect.currentframe()))
    markup = types.ReplyKeyboardRemove()
    myschedule_records = await fetch_schedule(message=message)
    my_sched = get_my_schedules(myschedule_records)
    chat_id = message["from"]["id"]
    lang = await src.db.funcs.fetch_lang(message=message)
    # No schedules, return to break the flow of the func
    if len(myschedule_records) == 0:
        await bot.send_message(
            chat_id=chat_id,
            text=md.escape_md(
                "You have not any saved schedules"
                if lang == "English"
                else "Δεν υπάρχουν προγραμματισμένες αποστολές ειδήσεων"
            ),
            disable_web_page_preview=True,
            parse_mode=types.ParseMode.MARKDOWN_V2,
            reply_markup=markup,
        )
        return None
    async for _schedule in my_sched:
        b = await _schedule
        logger.info(f"{b=}")
        logger.info(f"{b.id=}")
        if isinstance(b.trigger, CronTrigger):
            # Example:
            # CronTrigger(year='*', month='*', day='*', week='*', day_of_week='
            # mon-fri', hour='0', minute='0', second='0',
            # start_time='2023-12-19T20:27:28.333450+02:00', timezone='Europe/Bucharest')
            sch_time = f"{b.trigger.start_time.timetz()}".split(".")[0]
            answer = f"id: {b.id}\n"
            answer += (
                f"category: {b.args[1]}" f"\nSchedule news at {sch_time} (London time)\nevery \n"
                if lang.get("lang") == "English"
                else f"Κατηγορία ειδήσεων: {b.args[1]}"
                f"\nΠρογραμματισμένη αποστολή στις {sch_time} (ώρα Λονδίνου)\nκάθε: "
            )
            answer += f"{b.trigger._fields[4]}"
            logger.debug(f"{(b.trigger.start_time)}")
        else:
            # IntervalTrigger
            sch_time = f"{b.trigger.start_time.time()}".split(".")[0]
            logger.debug(f"{b.trigger.start_time=}")
            answer = f"id: {b.id}\n"
            logger.debug(f"{lang=}")
            answer += (
                f"category: {(b.args[1])}\n"
                f"Schedule news at {sch_time}\nevery "
                f"{b.trigger.weeks} weeks | "
                f"{b.trigger.days} days | "
                f"{b.trigger.hours} hours"
                if lang.get("lang") == "English"
                else f"Κατηγορία ειδήσεων: {b.args[1]}\n"
                f"Προγραμματισμένη αποστολή στις {sch_time} (ώρα Λονδίνου)\nκάθε "
                f"{b.trigger.weeks} εβδομάδες | "
                f"{b.trigger.days} μέρες | "
                f"{b.trigger.hours} ώρες"
            )

        await bot.send_message(
            chat_id=chat_id,
            text=md.escape_md(answer),
            disable_web_page_preview=True,
            parse_mode=types.ParseMode.MARKDOWN_V2,
            reply_markup=markup,
        )


@dp.message_handler(commands=["del", "delete", "δελ", "δελε", "δελετε"])
@update_user
async def del_schedule(message: types.Message) -> None:
    """
    Deletes the schedule based on the id that exists in the reply message
    """
    log_func_name(thelogger=logger, fun_name=func_name(inspect.currentframe()))
    if message.__getitem__("reply_to_message"):
        target_id = message["reply_to_message"]["text"]
        target_id = (
            target_id.split("\ncategory")
            if "category " in target_id
            else target_id.split("\nΚατηγορία")
        )
        target_id = target_id[0].replace("id:", "").strip()
        logger.debug(f"{target_id=} to be deleted")
        await delete_target_schedule(target_id=target_id)
        logger.debug(f"Schedule was deleted ({target_id=})")


@dp.message_handler(commands=["delall", "deleteall", "δελαλλ", "δελεαλλ", "δελετεαλλ"])
@update_user
async def del_all_schedules(message: types.Message) -> None:
    """Deletes every saved schedules of the user"""
    myschedule_records = await fetch_schedule(message=message)
    # logger.info(f"{myschedule_records=}")
    my_sched = get_my_schedules(myschedule_records)
    async for _schedule in my_sched:
        b = await _schedule
        target_id = b.id
        await delete_target_schedule(target_id=target_id)
        logger.debug(f"Schedule was deleted ({target_id=})")


@dp.message_handler(lambda message: message.text)
@update_user
async def random_text(message: types.Message) -> None:
    """Just to update the user's info, if anything is sent to the bot"""
    log_func_name(thelogger=logger, fun_name=func_name(inspect.currentframe()))
    pass
