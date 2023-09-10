"""
This module contains the code for the Actor who scrapes the news category
"""
import concurrent.futures
import random
import requests
import dataclasses

from typing import Any
from apify import Actor
from bs4 import BeautifulSoup, NavigableString

headers_list = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
    "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) "
    "Version/9.0.2 Safari/601.3.9",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/37.0.2062.94 "
    "Chrome/37.0.2062.94 Safari/537.36,"
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/101.0.4951.67 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/102.0.5005.63 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/101.0.4951.64 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/102.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/15.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/102.0.5005.61 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/15.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/101.0.4951.54 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:100.0) Gecko/20100101 Firefox/100.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/102.0.5005.62 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/102.0.5005.115 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.47",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/100.0.4896.75 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.39",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/101.0.4951.64 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/100.0.4896.127 Safari/537.36 OPR/86.0.4363.59",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/101.0.4951.54 Safari/537.36 Edg/101.0.1210.39",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.30",
]


def _header() -> dict[str, str]:
    """Picks and returns a random user agent from the list"""
    header = {"User-Agent": random.choice(headers_list)}
    print(f"Random header: {header}")
    return header


class CategoryScraper:
    """
    Connects to the url and scrapes the title, date.
    """

    def __init__(self, url, header, category=None, debug=False):
        self.news_list = []
        self.status_code = None
        self.r = None
        self.soup = None
        self.headers = header
        self.url = url
        self.category = category
        self.debug = debug
        self.check_url_and_iterate(self.url, self.headers)

    def check_url_and_iterate(self, url: str | list, header):
        """
        Checks if the url is a list of urls or an url and then proceeds.
        """
        self.connect_to_url(url, header)
        self.soup_the_request(request=self.r)
        self.scrape_the_soup()

    def connect_to_url(self, url, header):
        """
        Connects to the url using header
        """
        try:
            if not self.debug:
                self.r = requests.get(url, headers=header)
                self.status_code = self.r.status_code
        except Exception as err:
            print(f"Error fetching the URL: {url}" f"\nError: {err}")

    def soup_the_request(self, request):
        """
        Makes a soup from the request using BeautifulSoup.
        :param request: The request object
        :return: None
        """
        try:
            if not self.debug:
                self.soup = BeautifulSoup(request.text, "html.parser")  # Otherwise, self.r.text
        except Exception as err:
            print(f"Could not parse the html: {self.url}" f"\nError: {err}")

    def scrape_the_soup(self):
        """
        Scrapes the soup
        :return: None
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
            if self.category in ("Anaskopisi", "anaskopisi"):
                for div in self.soup.find_all("div", class_="m-item grid-item col-md-6"):
                    try:
                        executor.submit(self.iterate_div_for_anaskopisi, div)
                    except Exception as err:
                        print(err)
            else:
                for div in self.soup.find_all("div", class_="col-md-8 archive-item"):
                    try:
                        executor.submit(self.iterate_div, div)
                    except Exception as err:
                        print(f"SubPageReader Error: {err}")

    def iterate_div(self, div: Any):
        """
        Iterates div from the soup and scrapes the data

        :param div: The div object from the soup
        :return: None
        """
        temp_list = []
        title = ""
        link = ""
        for a in div.find_all("h3"):
            # print(a.text)
            for b in a.find_all("a", href=True, rel=True):
                # print(b.text)
                # print(f"url: {b['href']}, Title: {b['rel']}")
                link = b["href"].strip()
                for num, word in enumerate(b["rel"]):
                    if num != 0:  # Do not include a space in front of the first word
                        title += " "
                    title += word
                title.strip()
                temp_list.append(title)
                temp_list.append(link)
                news = NewsDataclass(url=link, title=title)
                self.news_list.append(news)

    def iterate_div_for_anaskopisi(self, div: Any):
        """
        Iterates div from the soup and scrapes the data for tpp.tv
        """
        temp_list = []
        title = ""
        link = ""

        for a in div.find_all("h3"):
            # print(f'a: {a.text}')
            for b in a.find_all("a", href=True):
                # <a href="https://thepressproject.gr/anaskopisi-s08e32-katataxi-eleftherias-tou-typou/">
                # ΑΝΑΣΚΟΠΗΣΗ S08E32: ΚΑΤΑΤΑΞΗ ΕΛΕΥΘΕΡΙΑΣ ΤΟΥ ΤΥΠΟΥ</a>
                link = b["href"].strip()
                # print(f"b: {b.text} {len(b.text)} {link} {len(link)}")
                title = b.text  # .replace("ΑΝΑΣΚΟΠΗΣΗ ", "").strip()
                temp_list.append(title)
                temp_list.append(link)

                self.news_list.append(NewsDataclass(url=link, title=title))


@dataclasses.dataclass
class NewsDataclass:
    """
    A Dataclass containing the scraped info.
    """

    url: str = ""
    main_content: str = ""
    summary: str = ""
    title: str = ""
    debug: bool = True

    def __str__(self):
        return f'Name:"{self.url}"'


async def main():
    async with Actor:
        # Read the Actor input
        actor_input = await Actor.get_input() or {}
        start_urls = actor_input.get(
            "start_urls"
        )  # , [{'url': 'https://thepressproject.gr/?s=tsipras&submit=Search'}])
        actor_input.get("max_depth", 1)
        Actor.log.info(f"start_urls: {start_urls}")

        print(f"start_urls: {start_urls}")
        if not start_urls:
            Actor.log.info("No start URLs specified in actor input, exiting...")
            await Actor.exit()

        # Enqueue the starting URLs in the default request queue
        default_queue = await Actor.open_request_queue()
        for start_url in start_urls:
            if not isinstance(start_url.get("url"), NavigableString):
                url = start_url.get("url")
                Actor.log.info(f"Enqueuing {url} ...")
                await default_queue.add_request({"url": url, "userData": {"depth": 0}})

        # Process the requests in the queue one by one
        while request := await default_queue.fetch_next_request():
            url = request["url"]

            Actor.log.info(f"Scraping {url} ...")

            try:
                search_results = CategoryScraper(header=_header(), url=url, debug=False)
                # Push the title of the page into the default dataset
                # title = soup.title.string if soup.title else None
                dict_to_push = {}
                for _dataclass in search_results.news_list:
                    dict_to_push[_dataclass.title] = _dataclass.url
                await Actor.push_data({"results_total": dict_to_push})
            except Exception:
                Actor.log.exception(f"Cannot extract data from {url}.")
            finally:
                # Mark the request as handled, so it's not processed again
                await default_queue.mark_request_as_handled(request)


if __name__ == "__main__":
    url = "https://thepressproject.gr/category/politics/"
    search_results = CategoryScraper(header=_header(), url=url)
    print(search_results.news_list)
