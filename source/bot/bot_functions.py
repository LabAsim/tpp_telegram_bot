"""A module containing the Bot"""

import logging
from aiogram import types, md
from source.bot.apify_actor import call_apify_actor, synthesize_url, convert_category_str_to_url
from source.bot.bot_dispatcher import dp, _bot


@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    """
    :param message: The input command
    """
    # sends welcome message after start

    await message.answer(md.escape_md('👋 Hello! Please select your language.'
                                      '\n👋 Γεια! Διάλεξε τι γλώσσα επιλογής σου'),
                         reply_markup=_bot.lang_kb)


@dp.message_handler(lambda message: message.text in ("English 👍", "Greek 🤝"))
async def save_language(message: types.Message) -> None:
    """Saves the language preference of the target user"""
    print(message)
    user_id = message["from"]["id"]
    lang = message.text.strip("👍").strip("🤝").strip()
    try:
        _bot.settings[f"{user_id}"]["lang"] = lang
    except KeyError:
        _bot.settings[f"{user_id}"] = {}
        _bot.settings[f"{user_id}"]["lang"] = lang
    print(f"{_bot.settings}")
    _bot.save_all_settings()
    markup = types.ReplyKeyboardRemove()
    if _bot.settings[f"{user_id}"]["lang"] == "English":
        await message.answer("Language preference is saved 👍", reply_markup=markup)
    else:
        await message.answer("Η επιλογή γλώσσας αποθηκεύτηκε 👍", reply_markup=markup)
    await show_help(message=message)


@dp.message_handler(commands=['lang', "language"])
async def choose_language(message: types.message):
    """Choose and saves the language preference of the user"""
    print(message)
    await message.answer(md.escape_md('👋 Hello! Please select your language.'
                                      '\n👋 Γεια! Διάλεξε τι γλώσσα επιλογής σου'),
                         reply_markup=_bot.lang_kb)


@dp.message_handler(commands=['help'])
async def show_help(message: types.Message):
    """
        Shows the help
        """
    user_id = message["from"]["id"]
    if _bot.settings[f"{user_id}"]["lang"] == "English":
        answer = md.text(md.bold('\n👇 -- The command list -- 👇\n'),
                         '\n• /search or /s ',
                         md.escape_md('\n\n\t\t\tArticle search based on a keyword'),
                         '\n\n\t\t\tExample:\t/search ΒΙΟΜΕ',
                         '\n',
                         '\n• /category or /c  ',
                         md.escape_md('\n\n\t\t\tSearch the latest news of the category'),
                         md.escape_md('\n\n\t\t\tExample:\t/category Newsroom'),
                         md.escape_md('\n\t\t\tExample:\t/category news'),
                         md.escape_md('\n\n\t\t\tValid categories:'),
                         md.escape_md('\n\t\t\t\t\t\tNews[room]'),
                         md.escape_md('\n\t\t\t\t\t\tPol[itics]'),
                         md.escape_md('\n\t\t\t\t\t\tEco[nomy]'),
                         md.escape_md('\n\t\t\t\t\t\tInter[national]'),
                         md.escape_md('\n\t\t\t\t\t\tRepo[rtage]'),
                         md.escape_md('\n\t\t\t\t\t\tAna[lysis]'),
                         md.escape_md('\n\t\t\t\t\t\tCul[ture]'),
                         md.escape_md('\n\t\t\t\t\t\tAna[skopisi]'),
                         md.escape_md('\n\t\t\t\t\t\t[tpp.]radio'),
                         md.escape_md('\n\t\t\t\t\t\t[tpp.]tv'),
                         md.escape_md('\n'),
                         '\n• /language or /lang',
                         md.escape_md('\n\n\t\t\tChoose your preferred language'),
                         md.escape_md('\n\n• /help : Prints this help text'),
                         '\n'
                         )
    else:
        answer = md.text(md.bold('\n👇 -- Η λίστα με όλες τις εντολές -- 👇\n'),
                         '\n• /search ή /s ',
                         md.escape_md('\n\n\t\t\tΑναζήτηση άρθρων βάσει λέξης κλειδί.'),
                         '\n\n\t\t\tΠαράδειγμα:\t/search ΒΙΟΜΕ',
                         '\n',
                         '\n• /category ή /c  ',
                         md.escape_md('\n\n\t\t\tΑναζήτηση τελευταίων άρθρων συγκεκριμένης κατηγορίας.'),
                         md.escape_md('\n\n\t\t\tΠαράδειγμα:\t/category Newsroom'),
                         md.escape_md('\n\n\t\t\tΚατηγορίες:'),
                         md.escape_md('\n\t\t\t\t\t\tNews[room]'),
                         md.escape_md('\n\t\t\t\t\t\tPol[itics]'),
                         md.escape_md('\n\t\t\t\t\t\tEco[nomy]'),
                         md.escape_md('\n\t\t\t\t\t\tInter[national]'),
                         md.escape_md('\n\t\t\t\t\t\tRepo[rtage]'),
                         md.escape_md('\n\t\t\t\t\t\tAna[lysis]'),
                         md.escape_md('\n\t\t\t\t\t\tCul[ture]'),
                         md.escape_md('\n\t\t\t\t\t\tAna[skopisi]'),
                         md.escape_md('\n\t\t\t\t\t\t[tpp.]radio'),
                         md.escape_md('\n\t\t\t\t\t\t[tpp.]tv'),
                         md.escape_md('\n'),
                         '\n• /language ή /lang',
                         md.escape_md('\n\n\t\t\tΔιάλεξε τη γλώσσα της επιλογής σου'),
                         md.escape_md('\n\n• /help : Τυπώνει αυτό το βοηθητικό κείμενο'),
                         '\n'
                         )
    await message.answer(answer)


@dp.message_handler(commands=['search', 's', 'σ'])
async def respond(message: types.Message):
    """Searches based on the user's input and replies with the search results"""
    logging.info(f"{message.from_user.first_name}: {message.text}")
    # Reset the counter
    _bot.page_number = 1
    _bot.search_keyword = message.text.strip().replace("/search", "").strip()
    _bot.search_keyword = _bot.search_keyword.strip().replace("/s", "").strip()
    _bot.search_keyword = _bot.search_keyword.strip().replace("/σ", "").strip()
    url = synthesize_url(keyword=_bot.search_keyword, page_number=1)
    # Add 1 one to the counter
    _bot.page_number += 1
    _bot.search_results = call_apify_actor(actor="athletic_scraper/my-actor",
                                           url=url, token=_bot.apify_token)["results_total"]
    answer = md.text()
    for result_dict_key in list(_bot.search_results.keys()):
        title = result_dict_key
        url = _bot.search_results[result_dict_key]
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


@dp.message_handler(lambda message: "arbitrary text, it does not mean anything" == message.text)
async def to_search_next_page(message: types.Message) -> None:
    """
    Asks the user whether to search the next page
    """

    # Configure ReplyKeyboardMarkup
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    user_id = message["from"]["id"]

    if _bot.settings[f"{user_id}"]["lang"] == "English":
        markup.add("Yes 🆗", "No 👎")
        await message.reply("Do you want to search the next page?", reply_markup=markup)
    else:
        markup.add("Ναι 🆗", "Όχι 👎")
        await message.reply("Θέλετε να συνεχίσετε την αναζήτηση στην επόμενη σελίδα;", reply_markup=markup)


@dp.message_handler(lambda message: "Yes 🆗" == message.text)
@dp.message_handler(lambda message: "Ναι 🆗" == message.text)
async def search_next_page(message: types.Message) -> None:
    """Searches the next page"""
    user_id = message["from"]["id"]
    # Check if the keyword is empty and the page number is 1.
    # If True, then prompt to search something first and stop the function.
    if _bot.search_keyword == "" and _bot.page_number == 1:
        markup = types.ReplyKeyboardRemove()
        if _bot.settings[f"{user_id}"]["lang"] == "English":
            await message.answer(text=md.escape_md("Nothing to search."
                                                   "\nRepeat the search command /search <keyword>"),
                                 reply_markup=markup)
        else:
            await message.answer(text=md.escape_md("\nΕπαναλάβετε την αναζήτηση με την εντολή /search <λέξη κλειδί>"),
                                 reply_markup=markup)
        return None
    url = synthesize_url(keyword=_bot.search_keyword, page_number=_bot.page_number)
    # Add 1 to the counter
    _bot.page_number += 1
    # Fetch the results
    _bot.search_results = call_apify_actor(url=url, token=_bot.apify_token,
                                           actor="athletic_scraper/my-actor")["results_total"]
    answer = ""
    for result_dict_key in list(_bot.search_results.keys()):
        title = result_dict_key
        url = _bot.search_results[result_dict_key]
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
        reply_to_empty_results = f"There are not any more results for the keyword: {_bot.search_keyword}"
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
    if _bot.search_keyword != "":
        if _bot.settings[f"{user_id}"]["lang"] == "English":
            await message.answer(f"Search for '{_bot.search_keyword}' is ended", reply_markup=markup)
        else:
            await message.answer(f"Η αναζήτηση για τον όρο '{_bot.search_keyword}' τερματίστηκε", reply_markup=markup)
    else:
        if _bot.settings[f"{user_id}"]["lang"] == "English":
            await message.answer(f"Search is ended", reply_markup=markup)
        else:
            await message.answer(f"Η αναζήτηση τερματίστηκε", reply_markup=markup)
    # Delete the keyword.
    _bot.search_keyword = ""
    # Reset the page number
    _bot.page_number = 1


@dp.message_handler(commands=['category', "Category", "c", "κατηγορία", "κατηγορια", "κ", ])
async def search_category(message: types.Message):
    """
    Scrapes the provided news category athletic_scraper/category-actor
    """
    logging.info(f"{message.from_user.first_name}: {message.text}")
    # Reset the counter
    _bot.page_number = 1
    _bot.search_keyword = message.text.strip().replace("/category", "").strip()
    _bot.search_keyword = _bot.search_keyword.strip().replace("/c", "").strip()
    _bot.search_keyword = _bot.search_keyword.strip().replace("/κατηγορία", "").strip()
    _bot.search_keyword = _bot.search_keyword.strip().replace("/κατηγορια", "").strip()
    _bot.search_keyword = _bot.search_keyword.strip().replace("/κ", "").strip()

    url = convert_category_str_to_url(category_str=_bot.search_keyword)
    # If the url does not exist (it's empty string), stop the method
    if url == "":
        return None
    # Add 1 one to the counter
    _bot.page_number += 1
    _bot.search_results = call_apify_actor(actor="athletic_scraper/category-actor",
                                           url=url, token=_bot.apify_token)["results_total"]
    answer = md.text()
    for result_dict_key in list(_bot.search_results.keys()):
        title = result_dict_key
        url = _bot.search_results[result_dict_key]
        last_line = ("-" * 50)
        answer += md.text(
            md.text(""),
            md.bold((md.text(title))),
            md.text(md.escape_md(url)),
            md.text(md.escape_md(last_line)), sep="\n")
    # logging.debug(f"Answer forwarded to user:{answer}")
    markup = types.ReplyKeyboardRemove()
    # Reply to user
    await message.reply(answer, reply_markup=markup, disable_web_page_preview=True,
                        parse_mode=types.ParseMode.MARKDOWN_V2)
