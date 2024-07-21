import pytest

from griptape.artifacts import TextArtifact
from griptape.drivers import ProxyWebScraperDriver


class TestProxyWebScraperDriver:
    @pytest.fixture(autouse=True)
    def mock_client(self, mocker):
        mock_response = mocker.Mock()
        mock_response.text = "test_scrape"
        return mocker.patch("requests.get", return_value=mock_response)

    @pytest.fixture()
    def mock_client_error(self, mocker):
        return mocker.patch("requests.get", side_effect=Exception("test_error"))

    @pytest.fixture()
    def web_scraper(self, mocker):
        return ProxyWebScraperDriver(
            proxies={"http": "http://localhost:8080", "https": "http://localhost:8080"},
            params={"test_param": "test_param"},
        )

    def test_scrape_url(self, web_scraper, mock_client):
        output = web_scraper.scrape_url("https://example.com/")
        mock_client.assert_called_with("https://example.com/", proxies=web_scraper.proxies, test_param="test_param")
        assert isinstance(output, TextArtifact)
        assert output.value == "test_scrape"

    def test_scrape_url_error(self, web_scraper, mock_client_error):
        with pytest.raises(Exception, match="test_error"):
            web_scraper.scrape_url("https://example.com/")
        assert mock_client_error.called
