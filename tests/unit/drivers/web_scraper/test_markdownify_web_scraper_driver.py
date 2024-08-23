from textwrap import dedent

import pytest

from griptape.drivers.web_scraper.markdownify_web_scraper_driver import MarkdownifyWebScraperDriver


class TestMarkdownifyWebScraperDriver:
    @pytest.fixture(autouse=True)
    def mock_playwright(self, mocker):
        return mocker.patch("playwright.sync_api.sync_playwright").return_value

    @pytest.fixture(autouse=True)
    def mock_content(self, mock_playwright):
        mock_content = mock_playwright.__enter__.return_value.chromium.launch.return_value.__enter__.return_value.new_context.return_value.new_page.return_value.content
        mock_content.return_value = '<html><a href="foobar.com">foobar</a></html>'
        return mock_content

    @pytest.fixture()
    def web_scraper(self):
        return MarkdownifyWebScraperDriver()

    def test_scrape_url(self, web_scraper):
        artifact = web_scraper.scrape_url("https://example.com/")
        assert artifact.value == "[foobar](foobar.com)"

    def test_scrape_url_whitespace(self, web_scraper, mock_content):
        mock_content.return_value = dedent(
            """\
            <html>
                \t<br><br>
                <br>
                <h2>foo</h2>
                <br>
                <br>
                <ul>
                    <li>
                        bar:
                        <ul>
                            <li>baz</li>
                            <li>baz</li><br>\t<br>
                            <li>baz</li>
                        </ul>
                    </li>
                </ul><br>\t
            </html>
            """
        )
        artifact = web_scraper.scrape_url("https://example.com/")
        assert artifact.value == "foo\n---\n\n* bar:\n  + baz\n  + baz\n\n  + baz"

    def test_scrape_url_no_excludes(self):
        web_scraper = MarkdownifyWebScraperDriver(exclude_tags=[], exclude_classes=[], exclude_ids=[])
        artifact = web_scraper.scrape_url("https://example.com/")
        assert artifact.value == "[foobar](foobar.com)"

    def test_scrape_url_exclude_links(self):
        web_scraper = MarkdownifyWebScraperDriver(include_links=False)
        artifact = web_scraper.scrape_url("https://example.com/")
        assert artifact.value == "foobar"

    def test_scrape_url_exclude_tags(self, mock_content):
        mock_content.return_value = "<html><pow>pow</pow><wow>wow</wow></html>"
        web_scraper = MarkdownifyWebScraperDriver(exclude_tags=["wow"], exclude_classes=[], exclude_ids=[])
        artifact = web_scraper.scrape_url("https://example.com/")
        assert artifact.value == "pow"

    def test_scrape_url_exclude_classes(self, mock_content):
        mock_content.return_value = '<html><pow>pow</pow><wow class="now">wow</wow></html>'
        web_scraper = MarkdownifyWebScraperDriver(exclude_tags=[], exclude_classes=["now"], exclude_ids=[])
        artifact = web_scraper.scrape_url("https://example.com/")
        assert artifact.value == "pow"

    def test_scrape_url_exclude_ids(self, mock_content):
        mock_content.return_value = '<html><pow>pow</pow><wow id="cow">wow</wow></html>'
        web_scraper = MarkdownifyWebScraperDriver(exclude_tags=[], exclude_classes=[], exclude_ids=["cow"])
        artifact = web_scraper.scrape_url("https://example.com/")
        assert artifact.value == "pow"

    def test_scrape_url_raises_on_empty_string_from_playwright(self, web_scraper, mock_content):
        mock_content.return_value = ""

        with pytest.raises(Exception, match="can't access URL"):
            web_scraper.scrape_url("https://example.com/")

    def test_scrape_url_raises_on_none_from_playwright(self, web_scraper, mock_content):
        mock_content.return_value = None

        with pytest.raises(Exception, match="can't access URL"):
            web_scraper.scrape_url("https://example.com/")
