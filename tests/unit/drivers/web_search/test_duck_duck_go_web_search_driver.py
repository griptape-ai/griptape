import json

import pytest

from griptape.artifacts import ListArtifact
from griptape.drivers import DuckDuckGoWebSearchDriver


class TestDuckDuckGoWebSearchDriver:
    @pytest.fixture()
    def driver(self, mocker):
        mock_response = [
            {"title": "foo", "href": "bar", "body": "baz"},
            {"title": "foo2", "href": "bar2", "body": "baz2"},
        ]

        mocker.patch("duckduckgo_search.DDGS.text", return_value=mock_response)

        return DuckDuckGoWebSearchDriver()

    @pytest.fixture()
    def driver_with_error(self, mocker):
        mocker.patch("duckduckgo_search.DDGS.text", side_effect=Exception("test_error"))

        return DuckDuckGoWebSearchDriver()

    def test_search_returns_results(self, driver):
        results = driver.search("test")
        assert isinstance(results, ListArtifact)
        output = [json.loads(result.value) for result in results]
        assert len(output) == 2
        assert output[0]["title"] == "foo"
        assert output[0]["url"] == "bar"
        assert output[0]["description"] == "baz"

    def test_search_raises_error(self, driver_with_error):
        with pytest.raises(Exception, match="Error searching 'test' with DuckDuckGo: test_error"):
            driver_with_error.search("test")
