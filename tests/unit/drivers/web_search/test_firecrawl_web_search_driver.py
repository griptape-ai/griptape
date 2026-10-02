import pytest
from firecrawl.types import Document, DocumentMetadata, SearchResultWeb

from griptape.artifacts import ListArtifact
from griptape.drivers.web_search.firecrawl import FirecrawlWebSearchDriver


class TestFirecrawlWebSearchDriver:
    @pytest.fixture()
    def mock_firecrawl_client(self, mocker):
        return mocker.patch("firecrawl.Firecrawl")

    @pytest.fixture()
    def driver(self, mock_firecrawl_client, mocker):
        mock_response = mocker.Mock()
        mock_response.web = [
            SearchResultWeb(title="foo", url="bar", description="baz"),
            SearchResultWeb(title="foo", url="bar", description="baz"),
        ]
        mock_firecrawl_client.return_value.search.return_value = mock_response
        return FirecrawlWebSearchDriver(api_key="test")

    def test_client(self, driver, mock_firecrawl_client):
        assert driver.client == mock_firecrawl_client.return_value
        mock_firecrawl_client.assert_called_once_with(
            api_key="test", api_url="https://api.firecrawl.dev", origin="griptape"
        )

    def test_client_uses_api_url(self, mock_firecrawl_client):
        driver = FirecrawlWebSearchDriver(api_key="test", api_url="http://localhost:3002")
        _ = driver.client
        mock_firecrawl_client.assert_called_once_with(
            api_key="test", api_url="http://localhost:3002", origin="griptape"
        )

    def test_search_returns_results(self, driver, mock_firecrawl_client):
        results = driver.search("test")
        assert isinstance(results, ListArtifact)
        output = [result.value for result in results]
        assert len(output) == 2
        assert output[0] == {"title": "foo", "url": "bar", "description": "baz"}
        mock_firecrawl_client.return_value.search.assert_called_once_with("test", limit=5)

    def test_search_with_results_count(self, mock_firecrawl_client):
        driver = FirecrawlWebSearchDriver(api_key="test", results_count=10)
        driver.search("test")
        mock_firecrawl_client.return_value.search.assert_called_once_with("test", limit=10)

    def test_search_returns_markdown_for_scraped_results(self, mock_firecrawl_client, mocker):
        mock_response = mocker.Mock()
        mock_response.web = [
            Document(markdown="# foo", metadata=DocumentMetadata(title="foo", url="bar", description="baz")),
            Document(markdown="# foo", metadata=DocumentMetadata(title="foo", source_url="bar")),
        ]
        mock_firecrawl_client.return_value.search.return_value = mock_response
        driver = FirecrawlWebSearchDriver(api_key="test", params={"scrape_options": {"formats": ["markdown"]}})

        output = [result.value for result in driver.search("test")]

        assert output[0] == {"title": "foo", "url": "bar", "description": "baz", "markdown": "# foo"}
        assert output[1]["url"] == "bar"
        mock_firecrawl_client.return_value.search.assert_called_once_with(
            "test", limit=5, scrape_options={"formats": ["markdown"]}
        )

    def test_search_returns_other_scraped_formats(self, mock_firecrawl_client, mocker):
        mock_response = mocker.Mock()
        mock_response.web = [Document(summary="qux", metadata=DocumentMetadata(title="foo", url="bar"))]
        mock_firecrawl_client.return_value.search.return_value = mock_response
        driver = FirecrawlWebSearchDriver(api_key="test", params={"scrape_options": {"formats": ["summary"]}})

        output = [result.value for result in driver.search("test")]

        assert output[0] == {"title": "foo", "url": "bar", "description": None, "summary": "qux"}

    def test_search_handles_document_without_metadata(self, mock_firecrawl_client, mocker):
        mock_response = mocker.Mock()
        mock_response.web = [Document(markdown="# foo")]
        mock_firecrawl_client.return_value.search.return_value = mock_response
        driver = FirecrawlWebSearchDriver(api_key="test")

        output = [result.value for result in driver.search("test")]

        assert output[0] == {"title": None, "url": None, "description": None, "markdown": "# foo"}

    def test_search_handles_no_web_results(self, driver, mock_firecrawl_client):
        mock_firecrawl_client.return_value.search.return_value.web = None
        assert len(driver.search("test")) == 0

    def test_search_raises_error(self, driver, mock_firecrawl_client):
        mock_firecrawl_client.return_value.search.side_effect = Exception("test_error")
        with pytest.raises(Exception, match="test_error"):
            driver.search("test")

    def test_search_with_params(self, driver, mock_firecrawl_client):
        driver.params = {"tbs": "qdr:w"}
        driver.search("test", location="Germany")
        mock_firecrawl_client.return_value.search.assert_called_once_with(
            "test", limit=5, tbs="qdr:w", location="Germany"
        )
