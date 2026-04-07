import pytest

from griptape.drivers.web_scraper.trafilatura_web_scraper_driver import TrafilaturaWebScraperDriver


class TestTrafilaturaWebScraperDriver:
    @pytest.fixture(autouse=True)
    def _mock_fetch_url(self, mocker):
        # Through trial and error, I've found that include_links in trafilatura's extract does not work
        # if the body of the page is not long enough, which is why I'm adding an arbitrary number of
        # characters to the body.
        mocker.patch(
            "trafilatura.fetch_url"
        ).return_value = f'<!DOCTYPE html><html>{"x" * 243}<a href="foobar.com">foobar</a></html>'

    @pytest.fixture()
    def web_scraper(self):
        return TrafilaturaWebScraperDriver(include_links=True)

    def test_scrape_url(self, web_scraper):
        artifact = web_scraper.scrape_url("https://example.com/")
        assert "[foobar](foobar.com)" in artifact.value

    def test_scrape_url_exclude_links(self):
        web_scraper = TrafilaturaWebScraperDriver(include_links=False)
        artifact = web_scraper.scrape_url("https://example.com/")
        assert "[foobar](foobar.com)" not in artifact.value
        assert "foobar" in artifact.value

    def test_scrape_url_raises_when_extract_returns_empty_string(self, web_scraper, mocker):
        mocker.patch("trafilatura.extract").return_value = ""

        with pytest.raises(Exception, match="can't extract page"):
            web_scraper.scrape_url("https://example.com/")

    def test_scrape_url_raises_when_extract_returns_none(self, web_scraper, mocker):
        mocker.patch("trafilatura.extract").return_value = None

        with pytest.raises(Exception, match="can't extract page"):
            web_scraper.scrape_url("https://example.com/")
