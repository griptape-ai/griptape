class TestWebScraper:
    """
    https://docs.griptape.ai/en/latest/griptape-tools/official-tools/web-scraper/
    """

    def test_web_scraper(self):
        from griptape.tools import WebScraper

        scraper = WebScraper()

        assert scraper is not None
