import json
from apify_client import ApifyClient
from typing import Union
from saved_tokens import token_apify


def synthesize_url(keyword: str, page_number: Union[int, str] = 1) -> str:
    """Constructs the final url and returns it"""
    print(keyword)
    base_url = "https://thepressproject.gr/page/"
    base_url_preterm = "/?s="
    page_number = str(page_number)
    suffix_url = "&submit=Search"
    keyword = str(keyword)
    final_url = base_url + page_number + base_url_preterm + keyword + suffix_url
    print(f"Recreated url: {final_url}")
    return final_url.strip()


def call_apify_actor(url: str, token: str) -> dict:
    """Calls the apify actor to scrape the target url and
    return a dictionary with the results

    :param url: `str` : The url to be scraped.
    :param token: `str` : The token of the Apify platform.
    :return: A `dict` holding the scraped data as {title: url}
    """
    apify_client = ApifyClient(token=token, max_retries=2)
    actor_client = apify_client.actor('athletic_scraper/my-actor')  # .call()

    dic = {'start_urls': [{'url': f'{url}'}]}
    dic = json.dumps(dic)

    my_actor = actor_client.get()
    act = actor_client.call(run_input=dic, content_type='application/json', timeout_secs=120)
    # print("act")
    # for key in act.keys():
    #    print(key)
    # print(act)
    dataset_items = apify_client.dataset(act['defaultDatasetId']).list_items().items

    # print("dataset")
    for item in dataset_items:
        print(item)
    # print(dataset_items)
    if isinstance(dataset_items, list):
        return dataset_items[0]  # Currently it contains only one item


if __name__ == '__main__':
    url = synthesize_url(keyword="ΒΙΟΜΕ")
    results = call_apify_actor(url=url, token=token_apify)
    print(results)
