import json

import pytest
from pytest_mock import MockerFixture

from griptape.drivers import GoogleWebSearchDriver


class TestGoogleWebSearchDriver:
    @pytest.fixture()
    def driver(self, mocker: MockerFixture):
        mock_response = mocker.Mock()
        mocker.patch.object(
            mock_response, "json", return_value={"items": [{"title": "foo", "link": "bar", "snippet": "baz"}]}
        )
        mock_response.status_code = 200

        mocker.patch("requests.get", return_value=mock_response)

        return GoogleWebSearchDriver(api_key="test", search_id="test")

    @pytest.fixture()
    def driver_with_error(self, mocker: MockerFixture):
        mock_response = mocker.Mock()
        mock_response.status_code = 500
        mock_response.reason = "test_reason"
        mocker.patch("requests.get", return_value=mock_response)

        return GoogleWebSearchDriver(api_key="test", search_id="test")

    def test_search_returns_results(self, driver):
        results = driver.search("test")
        output = [json.loads(result.value) for result in results]
        assert len(output) == 1
        assert output[0]["title"] == "foo"
        assert output[0]["url"] == "bar"
        assert output[0]["description"] == "baz"

    def test_search_raises_error(self, driver_with_error):
        with pytest.raises(
            Exception, match="Google Search API returned an error with status code 500 and reason 'test_reason'"
        ):
            driver_with_error.search("test")
