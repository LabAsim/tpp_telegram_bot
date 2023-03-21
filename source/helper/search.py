import requests
from bs4 import BeautifulSoup
from typing import Union
from source.helper.newsdataclass import NewsDataclass


class SearchTerm:
    """
    Scrapes the url, title, summary and date from the TPP site for the given keyword.
    """

    def __init__(self, term: Union[str, float, int], page_number: int, debug: bool):
        self.soup = None
        self.response = None
        self.list = []  # Holds ALL the scraped news
        # Holds only the scraped news from one scraping call.
        # If the next page is scraped, it will hold only the new one scraped news.
        self.temporary_list = []
        self.base_url = "https://thepressproject.gr/page/"
        self.base_url_preterm = "/?s="
        self.page_number = str(page_number)
        self.suffix_url = "&submit=Search"
        "https://thepressproject.gr/page/2"
        self.term = str(term)
        self.final_url = self.base_url + self.page_number + self.base_url_preterm + self.term + self.suffix_url
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
            if h2_find:
                for a in item.find("h2"):
                    # print(f"{number}\t: {a}\n")
                    link = a['href'].strip()
                    title = a.text
            if p_find:
                for p in item.find("p"):
                    summary = p.text
                    # print(p.text)
            if date_find:
                for _date in item.find("div", class_="entry-meta"):
                    date = _date.text.strip()
                # print(_date.text)
            # The date = "" will raise an IndexError in Newsdataclass, but we don't care about the unixtimestamp
            # in this occasion. Thus, debug is set to False. It remains True, for the rest of the program which uses
            # the Newsdataclass
            self.list.append(NewsDataclass(url=link, title=title, date=date, summary=summary, debug=False))
            self.temporary_list.append(NewsDataclass(url=link, title=title, date=date, summary=summary, debug=False))

    def scrape_next_page(self):
        """Scrapes the next page. If it is the first time to be called, it scrapes the next one"""
        self.page_number = str(int(self.page_number) + 1)
        self.final_url = self.base_url + self.page_number + self.base_url_preterm + self.term + self.suffix_url
        self.connect_to_url()
        self.soup_the_request()
        self.scrape_data()
