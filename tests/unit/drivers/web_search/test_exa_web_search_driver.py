import pytest

from griptape.artifacts import ListArtifact
from griptape.drivers import ExaWebSearchDriver


class TestExaWebSearchDriver:
    @pytest.fixture()
    def mock_exa_client(self, mocker):
        return mocker.patch("exa_py.Exa")

    def mock_data(self, mocker):
        return mocker.MagicMock(title="foo", url="bar", highlights="baz", text="qux")

    @pytest.fixture()
    def driver(self, mock_exa_client, mocker):
        mock_response = mocker.Mock()
        mock_response.results = [self.mock_data(mocker), self.mock_data(mocker)]  # Make sure results is iterable
        mock_exa_client.return_value.search_and_contents.return_value = mock_response
        return ExaWebSearchDriver(api_key="test", highlights=True, use_auto_prompt=True)

    def test_search_returns_results(self, driver, mock_exa_client):
        results = driver.search("test")
        assert isinstance(results, ListArtifact)
        output = [result.value for result in results]
        assert len(output) == 2
        assert output[0]["title"] == "foo"
        assert output[0]["url"] == "bar"
        assert output[0]["highlights"] == "baz"
        assert output[0]["text"] == "qux"
        mock_exa_client.return_value.search_and_contents.assert_called_once_with(
            query="test", num_results=5, text=True, highlights=True, use_auto_prompt=True
        )

    def test_search_raises_error(self, driver, mock_exa_client):
        mock_exa_client.return_value.search_and_contents.side_effect = Exception("test_error")
        driver = ExaWebSearchDriver(api_key="test", highlights=True, use_auto_prompt=True)
        with pytest.raises(Exception, match="test_error"):
            driver.search("test")
        mock_exa_client.return_value.search_and_contents.assert_called_once_with(
            query="test", num_results=5, text=True, highlights=True, use_auto_prompt=True
        )

    def test_search_with_params(self, driver, mock_exa_client):
        driver.params = {"custom_param": "value"}
        driver.search("test", additional_param="extra")

        mock_exa_client.return_value.search_and_contents.assert_called_once_with(
            query="test",
            num_results=5,
            text=True,
            highlights=True,
            use_auto_prompt=True,
            custom_param="value",
            additional_param="extra",
        )
