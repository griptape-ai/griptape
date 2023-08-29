import re


class TestQueryAWebpage:
    """
    https://docs.griptape.ai/en/latest/examples/query-webpage/
    """

    def test_query_a_webpage(self):
        from griptape.artifacts import BaseArtifact
        from griptape.drivers import LocalVectorStoreDriver
        from griptape.loaders import WebLoader

        vector_store = LocalVectorStoreDriver()

        [
            vector_store.upsert_text_artifact(a, namespace="griptape")
            for a in WebLoader(max_tokens=100).load("https://www.griptape.ai")
        ]

        results = vector_store.query("creativity", count=3, namespace="griptape")

        values = [BaseArtifact.from_json(r.meta["artifact"]).value for r in results]

        result = "\n\n".join(values)

        assert re.search("tape", result, re.IGNORECASE)
