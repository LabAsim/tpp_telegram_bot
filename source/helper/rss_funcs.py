import feedparser
import logging

# https://medium.com/@jonathanmondaut/fetching-data-from-rss-feeds-in-python-a-comprehensive-guide-a3dc86a5b7bc
# https://rssfeed.gr/feeds.php

logger = logging.getLogger(__name__)

urls = {
    "kathimerinieng": "https://feeds.feedburner.com/ekathimerini/sKip",
    "naftemporiki": "http://www.naftemporiki.gr/rssFeed",
    "tovima": "http://www.tovima.gr/feed/",
    "meteogr": "http://www.meteo.gr/rss/news.cfm",
    "ert": "http://www.ert.gr/feed/",
    "documento": "https://www.documentonews.gr/rss",
    "tpp": "https://thepressproject.gr/feed/rss/",
    "efsyn": "https://www.efsyn.gr/rss.xml",
}

# feed = feedparser.parse(urls["ert"])
# print("Feed Title:", feed.feed.title)
# print("Feed Description:", feed.feed.description)
# print("Feed Link:", feed.feed.link)
# # for key,value in feed.items():
# #     print(key, value)
# for entry in feed.entries:
#     print("Entry Title:", entry.title)
#     print("Entry Link:", entry.link)
#     print("Entry Published Date:", entry.get("published"))
#     # print("Entry Summary:", entry.get("summary"))
#     # print(f"{entry.summary_detail=}")
#     print("\n")


async def fetch_news(target: str) -> list:
    """Fetches the news from `target`"""

    feed = feedparser.parse(urls[f"{target}"])

    results = [entry for entry in feed.entries]

    return results
