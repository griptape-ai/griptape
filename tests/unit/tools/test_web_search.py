from griptape.artifacts import BaseArtifact, ErrorArtifact
from griptape.tools import WebSearch
from pytest import fixture
import json


class TestWebSearch:
    @fixture
    def websearch_tool(self, mocker):
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"title": "foo", "link": "bar", "snippet": "baz"}]}
        mocker.patch("requests.get", return_value=mock_response)

        return WebSearch(google_api_key="foo", google_api_search_id="bar")

    @fixture
    def websearch_tool_with_error(self, mocker):
        mock_response = mocker.Mock()
        mock_response.status_code = 500
        mocker.patch("requests.get", return_value=mock_response)

        return WebSearch(google_api_key="foo", google_api_search_id="bar")

    def test_search(self, websearch_tool):
        assert isinstance(websearch_tool.search({"values": {"query": "foo bar"}}), BaseArtifact)
        assert json.loads(websearch_tool.search({"values": {"query": "foo bar"}}).value[0].value) == {
            "title": "foo",
            "url": "bar",
            "description": "baz",
        }

    def test_search_with_error(self, websearch_tool_with_error):
        assert isinstance(websearch_tool_with_error.search({"values": {"query": "foo bar"}}), ErrorArtifact)
