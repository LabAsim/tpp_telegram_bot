'''
@self.dp.message_handler(commands=['search'])
        async def respond_deprecated(message: types.Message):
            """Searches based on the user's input and replies with the search results
            It is used if the bot runs standalone.
            """
            logging.info(f"{message.from_user.first_name}: {message.text}")
            self.search_keyword = message.text.replace("/search", "")
            self.search_results = SearchTerm(term=self.search_keyword, page_number=1, debug=False)
            answer = md.text()
            for number, result_dataclass in enumerate(self.search_results.list):
                title = result_dataclass.title
                url = result_dataclass.url
                last_line = ("-" * 50)
                answer += md.text(
                    md.text(""),
                    md.bold(md.escape_md(title)),
                    md.text(md.escape_md(url)),
                    md.text(md.escape_md(last_line)), sep="\n")
            # print(f"{answer}")
            markup = types.ReplyKeyboardRemove()
            # Reply to user
            await message.reply(answer, reply_markup=markup, disable_web_page_preview=True,
                                parse_mode=types.ParseMode.MARKDOWN_V2)
            # Wait the for user's input
            await to_search_next_page(message=message)

async def search_next_page_deprecated(message: types.Message):
    """This function is used if the bot runs standalone"""
    if self.search_results:
        self.search_results.scrape_next_page()
    answer = md.text()
    for number, result_dataclass in enumerate(self.search_results.temporary_list):
        title = result_dataclass.title
        url = result_dataclass.url
        last_line = ("-" * 50)
        answer += md.text(
            md.text(""),
            md.bold(md.escape_md(title)),
            md.text(md.escape_md(url)),
            md.text(md.escape_md(last_line)), sep="\n")
    markup = types.ReplyKeyboardRemove()
    # Reply to user
    await message.reply(answer, reply_markup=markup, disable_web_page_preview=True,
                        parse_mode=types.ParseMode.MARKDOWN_V2)

async def _req(self):
    await asyncio.sleep(10)
    final_url = "https://telegram_bot-1-e9314129.deta.app/"
    response = requests.get(url=final_url)
    print(response.text)
'''