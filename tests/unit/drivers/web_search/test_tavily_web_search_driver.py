import json

import pytest

from griptape.artifacts import ListArtifact
from griptape.drivers import TavilyWebSearchDriver


class TestTavilyWebSearchDriver:
    @pytest.fixture()
    def driver(self, mocker):
        mock_response = {
            "results": [
                {"title": "foo", "url": "bar", "content": "baz"},
                {"title": "foo2", "url": "bar2", "content": "baz2"},
            ]
        }
        mock_tavily = mocker.Mock(
            search=lambda *args, **kwargs: mock_response,
        )
        mocker.patch("tavily.TavilyClient", return_value=mock_tavily)
        return TavilyWebSearchDriver(api_key="test")

    @pytest.fixture()
    def driver_with_error(self, mocker):
        def error(*args, **kwargs):
            raise Exception("test_error")

        mock_tavily = mocker.Mock(
            search=error,
        )
        mocker.patch("tavily.TavilyClient", return_value=mock_tavily)

        return TavilyWebSearchDriver(api_key="test")

    def test_search_returns_results(self, driver):
        results = driver.search("test")
        assert isinstance(results, ListArtifact)
        output = [json.loads(result.value) for result in results]
        assert len(output) == 2
        assert output[0]["title"] == "foo"
        assert output[0]["url"] == "bar"
        assert output[0]["content"] == "baz"

    def test_search_raises_error(self, driver_with_error):
        with pytest.raises(Exception, match="Error searching 'test' with Tavily: test_error"):
            driver_with_error.search("test")
