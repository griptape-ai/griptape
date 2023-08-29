import re


class TestTalkToAWebpage:
    """
    https://docs.griptape.ai/en/latest/examples/talk-to-a-webpage/
    """

    def test_talk_to_a_webpage(self):
        import io
        import requests
        from griptape.engines import VectorQueryEngine
        from griptape.loaders import PdfLoader
        from griptape.structures import Agent
        from griptape.tools import VectorStoreClient

        namespace = "attention"

        response = requests.get("https://arxiv.org/pdf/1706.03762.pdf")
        engine = VectorQueryEngine()

        engine.vector_store_driver.upsert_text_artifacts(
            {namespace: PdfLoader().load(io.BytesIO(response.content))}
        )

        vector_store_tool = VectorStoreClient(
            description="Contains information about the Attention Is All You Need paper. "
            "Use it to answer any related questions.",
            query_engine=engine,
            namespace=namespace,
        )

        agent = Agent(tools=[vector_store_tool])

        result = agent.run("What is the title of this paper?")

        assert result.output is not None
        assert re.search("attention", result.output.to_text(), re.IGNORECASE)
