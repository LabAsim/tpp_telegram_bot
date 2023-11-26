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
    "bbc_top_stories": "http://feeds.bbci.co.uk/news/rss.xml",  # not implemented
    "bbc_top_stories_international": "http://feeds.bbci.co.uk/news/rss.xml?edition=int",
    "bbc_world": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "bbc_health": "http://feeds.bbci.co.uk/news/health/rss.xml",
    "bbc_science": "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    "bbc_tech": "http://feeds.bbci.co.uk/news/technology/rss.xml",  # not implemented
    "bbc_europe": "http://feeds.bbci.co.uk/news/world/europe/rss.xml",
    "guardian_europe": "https://www.theguardian.com/europe/rss",
    "guardian_middle_east": "https://www.theguardian.com/world/middleeast/rss",
    "guardian_world": "https://www.theguardian.com/world/rss",
    "reuters": "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best",
    "reuters_int": "https://www.reutersagency.com/feed/?taxonomy=best-regions&post_type=best",
    "reuters_politics": (
        "https://www.reutersagency.com/feed/?best-topics=political-general&post_type=best"
    ),
    "reuters_europe": "https://www.reutersagency.com/feed/?best-regions=europe&post_type=best",
    "reuters_news": (
        "https://www.reutersagency.com/feed/?best-types=reuters-news-first&post_type=best"
    ),
    "cnn": "http://rss.cnn.com/rss/cnn_latest.rss",
    "cnn_world": "http://rss.cnn.com/rss/edition_world.rss",
    "cnn_eu": "http://rss.cnn.com/rss/edition_europe.rss",
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
        case "bbc_world" | "bbcworld" | "bbcw" | "bbcwo" | "ββψ" | "ββσ" | "ββψγ":
            return "bbc_world"
        # Use of fmt is crucial here
        # as black unwraps the two lines and ruff points to a too long line
        # fmt: off
        case "bbc_top_stories_international" | "bbctopstoriesinternational" \
             | "bbctopint" | "bbctpint" | "ββψτοπιντ" | "ββστπιντ" | "ββψτπιντ":
            return "bbc_top_stories_international"
        case "bbc_europe" | "bbceurope" | "bbceu" | "bbce" | "ββψευ" | "ββσευ" | "ββψεθ":
            return "bbc_europe"
        case "bbc_science" | "bbcscience" | "bbcsc" | "bbcs" |\
             "ββψσψ" | "ββσσψ" | "ββψσψ" | "ββσεπ":
            return "bbc_science"
        case "guardian_europe" | "guaeu" | "geu" | "γθεθ" | "γευ":
            return "guardian_europe"
        case "guardian_middle_east" | "guame" | "gme" | "γθμε" | "γμε":
            return "guardian_middle_east"
        case "guardian_world" | "guaw" | "gw" | "γθς" | "γγ":
            return "guardian_world"
        case "reuters" | "reuter" | "reu" | "ρεθτερσ" | "ρευ" | "ρεθ":
            return "reuters"
        case "reuters_int" | "reutersint" | "reuint" |\
             "ρεθτερσιντ" | "ρευιντ" | "ρεθιντ" | "ριντ" | "rint":
            return "reuters_int"
        case "reuters_pol" | "reuterspol" | "reupol" |\
             "ρεθτερσπολ" | "ρευπολ" | "ρεθπολ" | "rpol" | "ρπολ":
            return "reuters_politics"
        case "reuters_eu" | "reuterseu" | "reueu" |\
            "ρεθτερσευ" | "ρευευ" | "ρεθευ" | "reur" | "ρευρ" | "ρεθρ":
            return "reuters_europe"
        case "reuters_news" | "reutersnews" | "reunews" |\
             "ρεθτερσνιουζ" | "ρνιουζ" | "ρεθνιουζ" | "rnews" | "ρνιουζ":
            return "reuters_news"
        case "cnn":
            return command
        case "cnn_world" | "cnnw" | "ψννς" | "σννγ":
            return "cnn_world"
        case "cnn_eu" | "cnneu" | "ψννεθ" | "ψννευ":
            return "cnn_eu"
        case _:
            raise ValueError(f"Unknown command passed {command=}")
        # fmt: on
