import pytest

from griptape.artifacts import ListArtifact


class TestWebScraper:
    @pytest.fixture(autouse=True)
    def _mock_trafilatura_fetch_url(self, mocker):
        mocker.patch("trafilatura.fetch_url", return_value="<html>foobar</html>")

    @pytest.fixture()
    def scraper(self):
        from griptape.tools import WebScraperTool

        return WebScraperTool()

    def test_get_content(self, scraper):
        assert isinstance(
            scraper.get_content({"values": {"url": "https://github.com/griptape-ai/griptape"}}), ListArtifact
        )
