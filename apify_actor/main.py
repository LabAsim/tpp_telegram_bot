from urllib.parse import urljoin

import requests
from apify import Actor
from bs4 import BeautifulSoup, NavigableString

import dataclasses
import re
import time
import unicodedata
from datetime import datetime, timedelta
from typing import Any, Union


@dataclasses.dataclass
class NewsDataclass:
    """
    A Dataclass containing the scraped info.
    """
    url: str = ''
    main_content: str = ''
    summary: str = ''
    title: str = ''
    debug: bool = True

    def __post_init__(self):
        # Convert date to UNIX timestamp
        try:
            self.main_content = self.strip_ansi_characters(self.main_content)
            self.summary = self.strip_ansi_characters(self.summary)
        except Exception as err:
            raise err

    def __str__(self):
        return f'Name:"{self.url}"'

    def strip_ansi_characters(self, text=''):
        """
        https://stackoverflow.com/questions/48782529/exclude-ansi-escape-sequences-from-output-log-file
        https://www.tutorialspoint.com/How-can-I-remove-the-ANSI-escape-sequences-from-a-string-in-python
        """
        try:
            # ansi_re = re.compile(r'[^\x00-\x7F]+')
            # return re.sub(r'[^\x00-\x7F]+', ' ', text)
            '''text = text.encode("ascii", "ignore")
                        text = text.decode()
                        print(text)
                        return text'''
            #  γνωστό ότι\xa0τα ΜΜΕ\xa0θα ενημερώνοντ
            ansi_re = re.compile(r'\x1b\[[0-9;]*m')
            text = re.sub(ansi_re, ' ', text)
            ansi_re = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
            ansi_re = re.compile('([\\\]x[\w\d]{,3})')
            text = re.sub(ansi_re, ' ', text)
            # https://docs.python.org/3/library/unicodedata.html#unicodedata.normalize
            # https://stackoverflow.com/a/34669482

            return text

        except re.error as err:
            print(err)

    @staticmethod
    def date_to_unix(_date: str) -> Union[int, float]:
        """
        Converts and returns the date to unix timestamp
        :param _date: Date in various forms
        :return: Unix timestamp
        See also:
            examples: https://www.devdungeon.com/content/working-dates-and-times-python-3
        Python docs:
            time: https://docs.python.org/3/library/time.html
            datetime: https://docs.python.org/3/library/datetime.html
        """

        # Make sure it's a string. Date is a tuple containing the date and an integer from sorting function (sortby())
        # date = str(date[0]).strip()
        # Note that date is an attribute of this Dataclass. Do not override it.
        _date = str(_date)
        # If the date is in the form of "Πριν 6 ώρες/λεπτά"
        if re.match('[Ππ]ρ[ιίΙ]ν', _date):
            # Remove 'Πριν/πριν'
            # See docs: https://docs.python.org/3/library/re.html#re.sub
            _date = re.sub(pattern='[Ππ]ρ[ιίΙ]ν', repl="", string=_date).lstrip(' ')
            if 'δευ' in _date:  # "39 δευτερόλεπτα"
                date_now = datetime.now()
                _date = _date.split(' ')
                _date = float(_date[0].strip(" ́").strip())
                unix_date = date_now - timedelta(seconds=_date)
                unix_date = time.mktime(unix_date.timetuple())
                return unix_date
            elif 'λεπτ' in _date:  # "2 λεπτά"
                date_now = datetime.now()
                _date = re.sub(pattern='[Λλ]{,2}επτ[αΑάΆοοΟόΌ]{,1}', repl="", string=_date, flags=re.IGNORECASE).lstrip(
                    ' ')
                _date = float(_date.strip(" ́").strip())
                unix_date = date_now - timedelta(minutes=_date)
                unix_date = time.mktime(unix_date.timetuple())
                return unix_date
            # elif re.search("[ωώ]ρ[εα][ς]?", date, flags=re.IGNORECASE):#"ώρ" in date: #  # "2 ώρες / ώρα" pass
            elif "ώρ" or "ωρ" or "ω΄ρ" in _date:
                date_now = datetime.now()
                _date = _date.split(" ")
                # date = re.sub(pattern="\s[ωώ]ρ[εα][ςΣ]?", repl="", string=date, flags=re.IGNORECASE).lstrip(' ')
                # date = date.strip('Πριν').strip("ώρα").strip("ώρες").strip()
                _date = float(_date[0].strip(" ́").strip())
                unix_date = date_now - timedelta(hours=_date)
                unix_date = time.mktime(unix_date.timetuple())
                return unix_date
            else:  # '1 ημέρα'
                date_now = datetime.now()
                _date = _date.split(' ')
                _date = float(_date[0])
                unix_date = date_now - timedelta(days=_date)
                unix_date = time.mktime(unix_date.timetuple())
                return unix_date
        # Date is in the form of "19/10/22"
        elif "/" in _date:
            _date = _date.split('/')
            year = int(_date[-1])
            month = int(_date[1])
            day = int(_date[0])
            unix_date = datetime(year, month, day)
            unix_date = time.mktime(unix_date.timetuple())
            return unix_date
        # The date is in the form of "Κυριακή 18 Δεκεμβρίου 2022"
        else:
            _date = _date.split()
            _date = _date[1:]  # Drop the name of the day
            year = int(_date[-1])
            month = NewsDataclass.month_str_to_int(_date[1])
            day = int(_date[0])
            unix_date = datetime(year, month, day)
            unix_date = time.mktime(unix_date.timetuple())
            # print(f"from a string: {unix_date}")
            return unix_date

    @staticmethod
    def month_str_to_int(month: str) -> int:
        """
        Converts a string based month to an integer based month. i.e. 'Δεκέμβρης' -> 12
        :param month: str
        :return: int
        """
        if re.match('Ιανου[αά]ρ[ιί][οuη]{,2}', month) or re.match('Γεν[αά]ρης', month):
            return 1
        elif re.match('Φεβρου[αά]ρ[ιί][οuη]{,2}', month) or re.match('Φλεβ[αά]ρης', month):
            return 2
        elif re.match('Μ[αά]ρτ[ιί][οuη]{,2}', month):
            return 3
        elif re.match('Απρ[ιί]λ[ιί][οuη]{,2}', month):
            return 4
        elif re.match('Μ[αά][ιί][οuη]{,2}', month):
            return 5
        elif re.match('Ιο[υύ]ν[ιί][οuη]{,2}', month):
            return 6
        elif re.match('Ιο[υύ][ιί][οuη]{,2}', month):
            return 7
        elif re.match('Α[υύ]γο[υύ]στου', month):
            return 8
        elif re.match('Σεπτ[εέ]μβρ[ιί][οuη]{,2}', month):
            return 9
        elif re.match('Οκτ[ωώ]βρ[ιί][οuη]{,2}', month):
            return 10
        elif re.match('Νο[εέ]μβρ[ιί][οuη]{,2}', month):
            return 11
        elif re.match('Δεκ[εέ]μβρ[ιί][οuη]{,2}', month):
            return 12

    @staticmethod
    def unix_to_datetime(unixtimestamp: int) -> str:
        """Converts unix timestampe to datetime format (DD/MM/YYYY)"""
        return datetime.utcfromtimestamp(unixtimestamp).strftime('%d/%m/%Y')

    def return_as_tuple(self):
        """
        Returns all attributes in a tuple.
        Alternative, just use dataclasses.astuple(object).
        See: https://docs.python.org/3/library/dataclasses.html#dataclasses.astuple
        """
        tuple_to_return = [self.date, self.url, self.main_content, self.summary, self.title, self.author,
                           self.author_url, self.date_unix, self.category]
        for number, a in enumerate(tuple_to_return):
            if a not in (self.date_unix, None):
                tuple_to_return[number] = unicodedata.normalize('NFKD', a)
                tuple_to_return[number] = tuple_to_return[number].strip('\'').strip("\"")
        return tuple(tuple_to_return)


class SearchTerm:
    """
    Scrapes the url, title, summary and date from the TPP site for the given keyword.
    """

    def __init__(self, final_url: str, debug: bool):
        self.soup = None
        self.response = None
        self.list = []  # Holds ALL the scraped news
        # Holds only the scraped news from one scraping call.
        # If the next page is scraped, it will hold only the new one scraped news.
        self.temporary_list = []
        '''self.base_url = "https://thepressproject.gr/page/"
        self.base_url_preterm = "/?s="
        self.page_number = str(page_number)
        self.suffix_url = "&submit=Search"
        "https://thepressproject.gr/page/2"
        self.term = str(term)
        self.final_url = self.base_url + self.page_number + self.base_url_preterm + self.term + self.suffix_url'''
        self.final_url = final_url
        self.debug = debug
        # Call the functions
        self.connect_to_url()
        self.soup_the_request()
        self.scrape_data()

    def connect_to_url(self):
        """Connects to the url and gets the response"""
        try:
            PROXY_URL = "http://proxy.server:3128"
            proxies = {"http": PROXY_URL}
            self.response = requests.get(self.final_url)  # , proxies=proxies)
        except requests.exceptions as err:
            print(err)

    def soup_the_request(self):
        """Makes a soup from self.response.text"""
        self.soup = BeautifulSoup(self.response.text, "html.parser")

    def scrape_data(self):
        """
        Scrapes the title, link, date and the summary. The scraped info is appended as a dataclass to a list.
        :return: None
        """
        # Clear the temporary list.
        self.temporary_list = []
        sample = self.soup.find_all("article")  # ("main", class_="site-main", id="main")
        for number, item in enumerate(sample):
            title = ""
            link = ""
            date = ""
            summary = ""
            h2_find = item.find("h2")
            p_find = item.find("p")
            date_find = item.find("div", class_="entry-meta")
            # These ifs exist to avoid Nones (No content from the search)
            if h2_find not in (None, ""):
                for a in item.find("h2"):
                    if not isinstance(a, NavigableString):
                        # print(f"{number}\t: {a}\n")
                        link = a['href'].strip()
                        title = a.text
                    else:
                        link = ""
                        title = ""
            if p_find not in (None, ""):
                for p in item.find("p"):
                    if not isinstance(p, NavigableString):
                        summary = p.text
                    else:
                        summary = ""
                # print(p.text)
            if date_find:
                for _date in item.find("div", class_="entry-meta"):
                    if not isinstance(_date, NavigableString):
                        date = _date.text.strip()
                    else:
                        date = "20/3/2023"
                # print(_date.text)
            # The date = "" will raise an IndexError in Newsdataclass, but we don't care about the unixtimestamp
            # in this occasion. Thus, debug is set to False. It remains True, for the rest of the program which uses
            # the Newsdataclass
            self.list.append(NewsDataclass(url=link, title=title, summary=summary, debug=False))
            self.temporary_list.append(NewsDataclass(url=link, title=title, summary=summary, debug=False))

    def scrape_next_page(self):
        """Scrapes the next page. If it is the first time to be called, it scrapes the next one"""
        self.page_number = str(int(self.page_number) + 1)
        self.final_url = self.base_url + self.page_number + self.base_url_preterm + self.term + self.suffix_url
        self.connect_to_url()
        self.soup_the_request()
        self.scrape_data()


async def main():
    async with Actor:
        # Read the Actor input
        actor_input = await Actor.get_input() or {}
        start_urls = actor_input.get('start_urls')#, [{'url': 'https://thepressproject.gr/?s=tsipras&submit=Search'}])
        max_depth = actor_input.get('max_depth', 1)
        Actor.log.info(f'start_urls: {start_urls}')

        print(f'start_urls: {start_urls}')
        if not start_urls:
            Actor.log.info('No start URLs specified in actor input, exiting...')
            await Actor.exit()

        # Enqueue the starting URLs in the default request queue
        default_queue = await Actor.open_request_queue()
        for start_url in start_urls:
            if not isinstance(start_url.get('url'), NavigableString):
                url = start_url.get('url')
                Actor.log.info(f'Enqueuing {url} ...')
                await default_queue.add_request({'url': url, 'userData': {'depth': 0}})

        # Process the requests in the queue one by one
        while request := await default_queue.fetch_next_request():
            url = request['url']
            depth = request['userData']['depth']
            Actor.log.info(f'Scraping {url} ...')

            try:
                search_results = SearchTerm(final_url=url, debug=False)
                # Push the title of the page into the default dataset
                # title = soup.title.string if soup.title else None
                dict_to_push = {}
                for _dataclass in search_results.list:
                    dict_to_push[_dataclass.title] = _dataclass.url

                await Actor.push_data({"results_total": dict_to_push})
            except:
                Actor.log.exception(f'Cannot extract data from {url}.')
            finally:
                # Mark the request as handled so it's not processed again
                await default_queue.mark_request_as_handled(request)
