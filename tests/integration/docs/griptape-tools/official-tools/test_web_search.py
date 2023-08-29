class TestWebSearch:
    """
    https://docs.griptape.ai/en/latest/griptape-tools/official-tools/web-search/
    """

    def test_web_search(self):
        import os
        from griptape.tools import WebSearch

        client = WebSearch(
            google_api_key=os.environ.get("GOOGLE_API_KEY"),
            google_api_search_id=os.environ.get("GOOGLE_API_SEARCH_ID"),
        )

        assert client is not None
