from griptape.artifacts import BaseArtifact
from griptape.tools import WebSearch


class TestWebSearch:
    def test_search(self):
        tool = WebSearch(google_api_key="foo", google_api_search_id="bar", off_prompt=False)

        assert isinstance(tool.search({"values": {"query": "foo bar"}}), BaseArtifact)
