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
    "kontra": "http://eksegersi.gr/?feed=rss2",
    "prin": "https://prin.gr/feed",
}


async def fetch_news(target: str) -> list:
    """Fetches the news from `target`"""

    feed = feedparser.parse(urls[f"{target}"])

    results = [entry for entry in feed.entries]

    return results


async def parse_commands_for_rssfeed(command: str) -> str:
    """Matches the command to the proper newspaper"""
    match command:
        case "efsyn" | "εφσυν":
            return "efsyn"
        case "kath" | "kat" | "kathimerini" | "καθ" | "κατ" | "καθη" | "καθημερινη":
            return "kathimerinieng"
        case "naftemporiki" | "naft" | "naf" | "ναφ" | "ναφτ" | "ναυτ" | "ναυ":
            return "naftemporiki"
        case "tovima" | "tov" | "τοβ" | "τοβημα":
            return "tovima"
        case "ert" | "ερτ":
            return "ert"
        case "documento" | "ντοκουμεντο" | "docu" | "δοκυ" | "doc" | "δοκ" | "ντοκ":
            return "documento"
        case "tpp" | "τππ":
            return "tpp"
        case "kontra" | "kon" | "κον" | "κοντρα" | "κόντρα":
            return "kontra"
        case "prin" | "πριν":
            return "prin"
        case _:
            raise ValueError(f"Unknown command passed {command=}")
