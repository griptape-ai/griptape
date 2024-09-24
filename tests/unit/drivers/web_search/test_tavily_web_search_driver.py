import pytest

from griptape.artifacts import ListArtifact
from griptape.drivers import TavilyWebSearchDriver


class TestTavilyWebSearchDriver:
    @pytest.fixture()
    def mock_tavily_client(self, mocker):
        return mocker.patch("tavily.TavilyClient")

    @pytest.fixture()
    def driver(self, mock_tavily_client):
        mock_response = {
            "results": [
                {"title": "foo", "url": "bar", "content": "baz"},
                {"title": "foo2", "url": "bar2", "content": "baz2"},
            ]
        }
        mock_tavily_client.return_value.search.return_value = mock_response
        return TavilyWebSearchDriver(api_key="test")

    def test_search_returns_results(self, driver, mock_tavily_client):
        results = driver.search("test")
        assert isinstance(results, ListArtifact)
        output = [result.value for result in results]
        assert len(output) == 2
        assert output[0]["title"] == "foo"
        assert output[0]["url"] == "bar"
        assert output[0]["content"] == "baz"
        mock_tavily_client.return_value.search.assert_called_once_with("test", max_results=5)

    def test_search_raises_error(self, mock_tavily_client):
        mock_tavily_client.return_value.search.side_effect = Exception("test_error")
        driver = TavilyWebSearchDriver(api_key="test")
        with pytest.raises(Exception, match="test_error"):
            driver.search("test")

    def test_search_with_params(self, mock_tavily_client):
        mock_response = {
            "results": [
                {"title": "custom", "url": "custom_url", "content": "custom_content"},
            ]
        }
        mock_tavily_client.return_value.search.return_value = mock_response

        driver = TavilyWebSearchDriver(api_key="test", params={"custom_param": "value"})
        results = driver.search("test", additional_param="extra")

        assert isinstance(results, ListArtifact)
        output = results[0].value
        assert output["title"] == "custom"
        assert output["url"] == "custom_url"
        assert output["content"] == "custom_content"

        mock_tavily_client.return_value.search.assert_called_once_with(
            "test", max_results=5, custom_param="value", additional_param="extra"
        )

    def test_custom_results_count(self, mock_tavily_client):
        mock_response = {
            "results": [{"title": f"title_{i}", "url": f"url_{i}", "content": f"content_{i}"} for i in range(5)]
        }
        mock_tavily_client.return_value.search.return_value = mock_response

        driver = TavilyWebSearchDriver(api_key="test", results_count=5)
        results = driver.search("test")

        assert isinstance(results, ListArtifact)
        assert len(results) == 5

        mock_tavily_client.return_value.search.assert_called_once_with("test", max_results=5)
