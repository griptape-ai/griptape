import json

import pytest

from griptape.artifacts import ListArtifact
from griptape.drivers.web_search.duck_duck_go import DuckDuckGoWebSearchDriver


class TestDuckDuckGoWebSearchDriver:
    @pytest.fixture()
    def driver(self, mocker):
        mock_response = [
            {"title": "foo", "href": "bar", "body": "baz"},
            {"title": "foo2", "href": "bar2", "body": "baz2"},
        ]
        mock_ddg = mocker.Mock(
            text=lambda *args, **kwargs: mock_response,
        )
        mocker.patch("duckduckgo_search.DDGS", return_value=mock_ddg)
        return DuckDuckGoWebSearchDriver()

    @pytest.fixture()
    def driver_with_error(self, mocker):
        def error(*args, **kwargs):
            raise Exception("test_error")

        mock_ddg = mocker.Mock(
            text=error,
        )
        mocker.patch("duckduckgo_search.DDGS", return_value=mock_ddg)

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
