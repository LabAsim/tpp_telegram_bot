"""
Tests for the apify_actor.py
"""
import unittest
import validators

from src.helper.rss_funcs import parse_commands_for_rssfeed, fetch_news, urls


class TestRssFuncs(unittest.IsolatedAsyncioTestCase):
    """See https://docs.python.org/3.11/library/unittest.html#unittest.IsolatedAsyncioTestCase"""

    async def test_parse_commands(self):
        # Εφσυν
        self.assertEqual(await parse_commands_for_rssfeed("efsyn"), "efsyn")
        self.assertEqual(await parse_commands_for_rssfeed("εφσυν"), "efsyn")
        # Καθημερινή
        self.assertEqual(await parse_commands_for_rssfeed("kath"), "kathimerinieng")
        self.assertEqual(await parse_commands_for_rssfeed("kat"), "kathimerinieng")
        self.assertEqual(await parse_commands_for_rssfeed("καθ"), "kathimerinieng")
        self.assertEqual(await parse_commands_for_rssfeed("κατ"), "kathimerinieng")
        self.assertEqual(await parse_commands_for_rssfeed("καθη"), "kathimerinieng")
        self.assertEqual(await parse_commands_for_rssfeed("καθημερινή"), "kathimerinieng")
        self.assertEqual(await parse_commands_for_rssfeed("καθημερινη"), "kathimerinieng")
        self.assertEqual(await parse_commands_for_rssfeed("kathimerini"), "kathimerinieng")
        self.assertEqual(await parse_commands_for_rssfeed("kathimerinieng"), "kathimerinieng")
        # Ναυτεμπορική
        self.assertEqual(await parse_commands_for_rssfeed("naftemporiki"), "naftemporiki")
        self.assertEqual(await parse_commands_for_rssfeed("naft"), "naftemporiki")
        self.assertEqual(await parse_commands_for_rssfeed("naf"), "naftemporiki")
        self.assertEqual(await parse_commands_for_rssfeed("ναφ"), "naftemporiki")
        self.assertEqual(await parse_commands_for_rssfeed("ναφτ"), "naftemporiki")
        self.assertEqual(await parse_commands_for_rssfeed("ναυτ"), "naftemporiki")
        self.assertEqual(await parse_commands_for_rssfeed("ναυ"), "naftemporiki")
        self.assertEqual(await parse_commands_for_rssfeed("nay"), "naftemporiki")
        self.assertEqual(await parse_commands_for_rssfeed("nayf"), "naftemporiki")
        self.assertEqual(await parse_commands_for_rssfeed("nayt"), "naftemporiki")
        self.assertEqual(await parse_commands_for_rssfeed("naut"), "naftemporiki")
        # ΤοΒήμα
        self.assertEqual(await parse_commands_for_rssfeed("tovima"), "tovima")
        self.assertEqual(await parse_commands_for_rssfeed("tov"), "tovima")
        self.assertEqual(await parse_commands_for_rssfeed("tovi"), "tovima")
        self.assertEqual(await parse_commands_for_rssfeed("τοβ"), "tovima")
        self.assertEqual(await parse_commands_for_rssfeed("τοβημα"), "tovima")
        self.assertEqual(await parse_commands_for_rssfeed("τοβήμα"), "tovima")
        self.assertEqual(await parse_commands_for_rssfeed("τοβη"), "tovima")
        # Ερτ
        self.assertEqual(await parse_commands_for_rssfeed("ert"), "ert")
        self.assertEqual(await parse_commands_for_rssfeed("ερτ"), "ert")
        # Ertnews
        self.assertEqual(await parse_commands_for_rssfeed("ertnews"), "ert_latest")
        self.assertEqual(await parse_commands_for_rssfeed("ερτνεςσ"), "ert_latest")
        self.assertEqual(await parse_commands_for_rssfeed("ερτνιουζ"), "ert_latest")
        self.assertEqual(await parse_commands_for_rssfeed("ertlatest"), "ert_latest")
        self.assertEqual(await parse_commands_for_rssfeed("ertn"), "ert_latest")
        self.assertEqual(await parse_commands_for_rssfeed("ertla"), "ert_latest")
        # Documento
        self.assertEqual(await parse_commands_for_rssfeed("documento"), "documento")
        self.assertEqual(await parse_commands_for_rssfeed("ντοκουμεντο"), "documento")
        self.assertEqual(await parse_commands_for_rssfeed("docu"), "documento")
        self.assertEqual(await parse_commands_for_rssfeed("δοκυ"), "documento")
        self.assertEqual(await parse_commands_for_rssfeed("doc"), "documento")
        self.assertEqual(await parse_commands_for_rssfeed("δοκ"), "documento")
        self.assertEqual(await parse_commands_for_rssfeed("ντοκ"), "documento")
        # TPP
        self.assertEqual(await parse_commands_for_rssfeed("tpp"), "tpp")
        self.assertEqual(await parse_commands_for_rssfeed("τππ"), "tpp")
        # Kontra
        self.assertEqual(await parse_commands_for_rssfeed("kontra"), "kontra")
        self.assertEqual(await parse_commands_for_rssfeed("kon"), "kontra")
        self.assertEqual(await parse_commands_for_rssfeed("κον"), "kontra")
        self.assertEqual(await parse_commands_for_rssfeed("κοντρα"), "kontra")
        self.assertEqual(await parse_commands_for_rssfeed("κόντρα"), "kontra")
        # Πριν
        self.assertEqual(await parse_commands_for_rssfeed("πριν"), "prin")
        self.assertEqual(await parse_commands_for_rssfeed("prin"), "prin")
        # Reporters United
        self.assertEqual(await parse_commands_for_rssfeed("ru"), "reporters_united")
        self.assertEqual(await parse_commands_for_rssfeed("repun"), "reporters_united")
        self.assertEqual(await parse_commands_for_rssfeed("reportersunited"), "reporters_united")
        self.assertEqual(await parse_commands_for_rssfeed("reporters_united"), "reporters_united")
        self.assertEqual(await parse_commands_for_rssfeed("ρθ"), "reporters_united")
        self.assertEqual(await parse_commands_for_rssfeed("ρυ"), "reporters_united")
        self.assertEqual(await parse_commands_for_rssfeed("ru"), "reporters_united")
        self.assertEqual(await parse_commands_for_rssfeed("rurepo"), "reporters_united")
        self.assertEqual(await parse_commands_for_rssfeed("rur"), "reporters_united")
        self.assertEqual(await parse_commands_for_rssfeed("ρθρ"), "reporters_united")
        self.assertEqual(await parse_commands_for_rssfeed("ρυρ"), "reporters_united")
        self.assertEqual(
            await parse_commands_for_rssfeed("reporters_united_reportage"), "reporters_united"
        )
        # BBC world
        self.assertEqual(await parse_commands_for_rssfeed("bbc_world"), "bbc_world")
        self.assertEqual(await parse_commands_for_rssfeed("bbcworld"), "bbc_world")
        self.assertEqual(await parse_commands_for_rssfeed("bbcw"), "bbc_world")
        self.assertEqual(await parse_commands_for_rssfeed("bbcwo"), "bbc_world")
        self.assertEqual(await parse_commands_for_rssfeed("ββψ"), "bbc_world")
        self.assertEqual(await parse_commands_for_rssfeed("ββσ"), "bbc_world")
        self.assertEqual(await parse_commands_for_rssfeed("ββψγ"), "bbc_world")
        self.assertEqual(await parse_commands_for_rssfeed("bbc"), "bbc_world")

    async def test_fetch_news_tpp(self):
        target = "tpp"
        results = await fetch_news(target)
        self.assertIsInstance(results, list)
        self.assertIs(len(results), 10)
        for entry in results:
            self.assertIsInstance(entry.title, str)
            self.assertTrue(validators.url(entry.link))

    async def test_fetch_news(self):
        targets = list(urls.keys())
        for target in targets:
            results = await fetch_news(target)
            self.assertIsInstance(results, list)
            for entry in results:
                self.assertIsInstance(entry.title, str)
                self.assertTrue(validators.url(entry.link))


if __name__ == "__main__":
    unittest.main()
