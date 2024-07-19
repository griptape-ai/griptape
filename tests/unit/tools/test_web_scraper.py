import pytest

from griptape.artifacts import ListArtifact
from griptape.tools import WebScraper


class TestWebScraper:
    @pytest.fixture()
    def scraper(self, mocker):
        web_scraper = WebScraper()

        mocker.patch.object(web_scraper.web_loader.web_scraper_driver, "scrape_url", return_value=ListArtifact([]))

        return web_scraper

    def test_get_content(self, scraper):
        assert isinstance(
            scraper.get_content({"values": {"url": "https://github.com/griptape-ai/griptape"}}), ListArtifact
        )
