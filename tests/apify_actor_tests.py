"""
Tests for the apify_actor.py
"""
import unittest
import validators

from saved_tokens import token_apify
from source.bot.apify_actor import convert_category_str_to_url, synthesize_url, call_apify_actor


class TestApifyActor(unittest.TestCase):

    def test_convert_category_str_to_url(self):
        # Newsroom
        for a in ("Newsroom", "newsroom", "new", "n"):
            target_url = "https://thepressproject.gr/article_type/newsroom/"
            self.assertEqual(convert_category_str_to_url(a), target_url)
        # Politics
        for a in ("Politics", "Pol", "politics", "pol", "p",
                  "Πολιτική", "Πολιτικη", "πολιτικη", "πολιτική", "Πολ", "πολ", "π"):
            target_url = "https://thepressproject.gr/category/politics/"
            self.assertEqual(convert_category_str_to_url(a), target_url)
        # Economy
        for a in ("Economy", "economy", "eco", "e",
                  "Οικονομία", "Οικονομια", "οικονομία", "οικονομια", "οικ", "ο"):
            target_url = "https://thepressproject.gr/category/economy/"
            self.assertEqual(convert_category_str_to_url(a), target_url)
        # International
        for a in ("International", "international", "inter", "Διεθνή", "Διεθνη", "Δ", "δ"):
            target_url = "https://thepressproject.gr/category/international/"
            self.assertEqual(convert_category_str_to_url(a), target_url)
        # Analysis
        for a in ("Analysis", "analysis", "a", "Ανάλυση", "Αναλυση", "ανάλυση", "αναλυση", "αναλ"):
            target_url = "https://thepressproject.gr/article_type/analysis/"
            self.assertEqual(convert_category_str_to_url(a), target_url)
        # Anaskopisi
        for a in ("Ανασκόπηση", "Ανασκοπηση", "ανασκόπηση", "ανασκοπηση", "ανασ",
                  "Anaskopisi", "anaskopisi", "anas"):
            target_url = "https://thepressproject.gr/tv_show/anaskopisi/"
            self.assertEqual(convert_category_str_to_url(a), target_url)
        # Culture
        for a in ("Culture", "culture", "cul", "Πολιτιστμός", "Πολιτισμος", "πολιτισμός", "πολιτισμος",
                  "πολιτισ"):
            target_url = "https://thepressproject.gr/category/culture/"
            self.assertEqual(convert_category_str_to_url(a), target_url)
        # tpp.tv
        for a in ("tpp.tv", "tv"):
            target_url = "https://thepressproject.gr/article_type/tv/"
            self.assertEqual(convert_category_str_to_url(a), target_url)
        # tpp.radio
        for a in ("tpp.radio", "radio"):
            target_url = "https://thepressproject.gr/radio/"
            self.assertEqual(convert_category_str_to_url(a), target_url)
        for a in ("Reportage", "Repo", "rep", "reportage", "repo", "rep",
                  "Ρεπορταζ", "Ρεπορτάζ", "ρεπο", "ρεπ"):
            target_url = "https://thepressproject.gr/article_type/report/"
            self.assertEqual(convert_category_str_to_url(a), target_url)

    def test_synthesize_url(self):
        self.assertEqual("https://thepressproject.gr/page/1/?s=&submit=Search", synthesize_url(keyword=""))
        # The greek letters needs to be encoded in utf-8.
        # Otherwise, an error will be raised (UnicodeEncodeError: 'charmap' codec can't encode characters in position)
        # This can be adressed either by encode("utf-8")
        # or by changing the terminal encoding through Pycharm's settings.
        self.assertEqual("https://thepressproject.gr/page/1/?s=Τσίπρας&submit=Search".encode("utf-8"),
                         synthesize_url(keyword="Τσίπρας", debug=False).encode("utf-8"))
        for keyword in ("tsipras", "Τσίπρας", "Τσιπρας", "Koulis"):
            self.assertEqual(f"https://thepressproject.gr/page/1/?s={keyword}&submit=Search".encode("utf-8"),
                             synthesize_url(keyword=keyword, debug=False).encode("utf-8"))
        # Check 2nd page
        self.assertEqual("https://thepressproject.gr/page/2/?s=Τσίπρας&submit=Search",
                         synthesize_url(keyword="Τσίπρας", debug=False, page_number=2))

    def test_call_apify_actor_keyword_search(self):

        # Search ==> athletic_scraper/my-actor
        url = synthesize_url(keyword="Τσίπρας")
        results = call_apify_actor(token=token_apify, actor="athletic_scraper/my-actor", url=url)["results_total"]
        self.assertIsInstance(results, dict)
        self.assertIs(len(results), 10)
        for key, value in results.items():
            self.assertIsInstance(key, str)
            self.assertTrue(validators.url(value))

    def test_call_apify_actor_category_search(self):
        # Category ==> athletic_scraper/category-actor
        # Test the Culture category
        url = convert_category_str_to_url(category_str="cul")
        results = call_apify_actor(actor="athletic_scraper/category-actor",
                                   url=url, token=token_apify)["results_total"]
        self.assertIsInstance(results, dict)
        self.assertIs(len(results), 10)
        for key, value in results.items():
            self.assertIsInstance(key, str)
            self.assertTrue(validators.url(value))


if __name__ == '__main__':
    unittest.main(verbosity=0, buffer=True)
