import re


class TestVectorStoreClient:
    """
    https://docs.griptape.ai/en/latest/griptape-tools/official-tools/vector-store-client/
    """

    def test_tool_output_processor(self):
        from griptape.structures import Agent
        from griptape.tools import VectorStoreClient
        from griptape.loaders import WebLoader
        from griptape.engines import VectorQueryEngine

        engine = VectorQueryEngine()

        engine.upsert_text_artifacts(
            WebLoader().load("https://www.griptape.ai"), namespace="griptape"
        )

        vector_db = VectorStoreClient(
            description="This DB has information about the Griptape Python framework",
            query_engine=engine,
            namespace="griptape",
        )

        agent = Agent(tools=[vector_db])

        result = agent.run("what is Griptape?")

        assert result.output is not None
        assert re.search("tape", result.output.to_text(), re.IGNORECASE)
