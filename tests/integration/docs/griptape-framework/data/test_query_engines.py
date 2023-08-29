import re


class TestQueryEngines:
    """
    https://docs.griptape.ai/en/latest/griptape-framework/data/query-engines/
    """

    def test_vector_query_engine(self):
        from griptape.engines import VectorQueryEngine
        from griptape.loaders import WebLoader

        engine = VectorQueryEngine()

        engine.upsert_text_artifacts(
            WebLoader().load("https://www.griptape.ai"), namespace="griptape"
        )

        assert True

        result = engine.query("what is griptape?", namespace="griptape")

        assert result.value is not None
        assert re.search("tape", result.value, re.IGNORECASE)
