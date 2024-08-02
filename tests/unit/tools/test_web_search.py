import pytest

from griptape.artifacts import BaseArtifact, ErrorArtifact, TextArtifact
from griptape.tools import WebSearch


class TestWebSearch:
    @pytest.fixture()
    def websearch_tool(self, mocker):
        mock_response = TextArtifact("test_response")
        driver = mocker.Mock()
        mocker.patch.object(driver, "search", return_value=mock_response)

        return WebSearch(web_search_driver=driver)

    @pytest.fixture()
    def websearch_tool_with_error(self, mocker):
        mock_response = Exception("test_error")
        driver = mocker.Mock()
        mocker.patch.object(driver, "search", side_effect=mock_response)

        return WebSearch(web_search_driver=driver)

    def test_search(self, websearch_tool):
        assert isinstance(websearch_tool.search({"values": {"query": "foo bar"}}), BaseArtifact)
        assert websearch_tool.search({"values": {"query": "foo bar"}}).value == "test_response"

    def test_search_with_params(self, websearch_tool):
        assert isinstance(
            websearch_tool.search({"values": {"query": "foo bar", "params": {"key": "value"}}}), BaseArtifact
        )
        assert (
            websearch_tool.search({"values": {"query": "foo bar", "params": {"key": "value"}}}).value == "test_response"
        )

    def test_search_with_error(self, websearch_tool_with_error):
        assert isinstance(websearch_tool_with_error.search({"values": {"query": "foo bar"}}), ErrorArtifact)
        assert (
            websearch_tool_with_error.search({"values": {"query": "foo bar"}}).value
            == "Error searching 'foo bar' with Mock: test_error"
        )
