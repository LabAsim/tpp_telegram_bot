import json
import logging
import time

from apify_client import ApifyClient
from typing import Union
from src.helper.helper import timed_lru_cache


def convert_category_str_to_url(category_str: str) -> str:
    """Converts the string category to a valid url"""
    if category_str in ("Newsroom", "newsroom", "news", "new", "n"):
        return "https://thepressproject.gr/article_type/newsroom/"
    elif category_str in (
        "Politics",
        "Pol",
        "politics",
        "pol",
        "p",
        "Πολιτική",
        "Πολιτικη",
        "πολιτικη",
        "πολιτική",
        "Πολ",
        "πολ",
        "π",
    ):
        return "https://thepressproject.gr/category/politics/"
    elif category_str in (
        "Economy",
        "economy",
        "eco",
        "e",
        "Οικονομία",
        "Οικονομια",
        "οικονομία",
        "οικονομια",
        "οικ",
        "ο",
    ):
        return "https://thepressproject.gr/category/economy/"
    elif category_str in (
        "International",
        "international",
        "inter",
        "int",
        "Διεθνή",
        "Διεθνη",
        "Δ",
        "δ",
    ):
        return "https://thepressproject.gr/category/international/"
    elif category_str in (
        "Analysis",
        "analysis",
        "A",
        "a",
        "Α",
        "α",
        "Ανάλυση",
        "Αναλυση",
        "ανάλυση",
        "αναλυση",
        "αναλ",
    ):
        return "https://thepressproject.gr/article_type/analysis/"
    elif category_str in (
        "Ανασκόπηση",
        "Ανασκοπηση",
        "ανασκόπηση",
        "ανασκοπηση",
        "ανασ",
        "Anaskopisi",
        "anaskopisi",
        "anas",
    ):
        return "https://thepressproject.gr/tv_show/anaskopisi/"
    elif category_str in (
        "Culture",
        "Cul",
        "culture",
        "cul",
        "Πολιτιστμός",
        "Πολιτισμος",
        "πολιτισμός",
        "πολιτισμος",
        "πολιτισ",
    ):
        return "https://thepressproject.gr/category/culture/"
    elif category_str in (
        "Reportage",
        "Repo",
        "rep",
        "reportage",
        "repo",
        "rep",
        "Ρεπορταζ",
        "Ρεπορτάζ",
        "ρεπο",
        "ρεπ",
    ):
        return "https://thepressproject.gr/article_type/report/"
    elif category_str in ("tpp.tv", "tv"):
        return "https://thepressproject.gr/article_type/tv/"
    elif category_str in ("tpp.radio", "radio"):
        return "https://thepressproject.gr/article_type/radio"
    elif category_str in ("greece", "gre", "Ελλάδα", "Ελλαδα", "Ελλ"):
        return "https://thepressproject.gr/category/greece/"
    elif category_str in ("english", "English", "eng", "english", "αγγλικα", "αγγ"):
        return "https://thepressproject.gr/category/english/"
    else:
        logging.debug(f"'{category_str}' does not respond to any know category")
        return ""


def synthesize_url(keyword: str, page_number: Union[int, str] = 1, debug: bool = False) -> str:
    """Constructs the final url and returns it"""
    # print(keyword)
    base_url = "https://thepressproject.gr/page/"
    base_url_preterm = "/?s="
    page_number = str(page_number)
    suffix_url = "&submit=Search"
    keyword = str(keyword)
    final_url = base_url + page_number + base_url_preterm + keyword + suffix_url
    if debug:
        print(f"Recreated url: {final_url}")
    return final_url.strip()


@timed_lru_cache(minutes=10)
def call_apify_actor(actor: str, url: str, token: str) -> dict:
    """Calls the apify actor to scrape the target url and
    return a dictionary with the results
    :param actor: `str` : The actor name to be called.
    :param url: `str` : The url to be scraped.
    :param token: `str` : The token of the Apify platform.
    :return: A `dict` holding the scraped data as {title: url}
    """
    apify_client = ApifyClient(token=token, max_retries=3)
    actor_client = apify_client.actor(f"{actor}")  # .call()

    dic = {"start_urls": [{"url": f"{url}"}]}
    dic = json.dumps(dic)

    actor_client.get()
    act = actor_client.call(run_input=dic, content_type="application/json", timeout_secs=120)
    # print("act")
    # for key in act.keys():
    #    print(key)
    # print(act)
    dataset_items = apify_client.dataset(act["defaultDatasetId"]).list_items().items

    # print("dataset")
    for item in dataset_items:
        print(item)
    # print(dataset_items)
    if isinstance(dataset_items, list):
        return dataset_items[0]  # Currently it contains only one item


if __name__ == "__main__":
    try:
        import saved_tokens
    except ModuleNotFoundError:
        from src.helper.helper import EnvVars as saved_tokens
    while True:
        url = synthesize_url(keyword="ΒΙΟΜΕ")
        results = call_apify_actor(
            url="https://thepressproject.gr/article_type/radio",
            token=saved_tokens.TOKEN_APIFY,
            actor="athletic_scraper/my-actor",
        )
        print(results)
        time.sleep(1)
