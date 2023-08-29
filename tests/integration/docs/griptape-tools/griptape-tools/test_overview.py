import re


class TestOverview:
    """
    https://docs.griptape.ai/en/latest/griptape-tools/
    """

    def test_random_number_generator(self):
        import random
        from griptape.artifacts import TextArtifact
        from griptape.tools import BaseTool
        from griptape.utils.decorators import activity
        from schema import Schema, Literal, Optional

        class RandomNumberGenerator(BaseTool):
            @activity(
                config={
                    "description": "Can be used to generate random numbers",
                    "schema": Schema(
                        {
                            Optional(
                                Literal(
                                    "decimals",
                                    description="Number of decimals to round the random number to",
                                )
                            ): int
                        }
                    ),
                }
            )
            def generate(self, params: dict) -> TextArtifact:
                return TextArtifact(
                    str(round(random.random(), params["values"].get("decimals")))
                )

        rng_tool = RandomNumberGenerator()
        result = rng_tool.generate({"values": {"decimals": 2}})

        assert result.value is not None

    def test_web_loader(self):
        from griptape.drivers import LocalVectorStoreDriver
        from griptape.engines import VectorQueryEngine
        from griptape.loaders import WebLoader
        from griptape.structures import Agent
        from griptape.tools import VectorStoreClient

        namespace = "griptape-ai"
        vector_store = LocalVectorStoreDriver()
        query_engine = VectorQueryEngine(vector_store_driver=vector_store)
        vector_store_tool = VectorStoreClient(
            description="Contains information about the Griptape Framework "
            "from www.griptape.ai",
            query_engine=query_engine,
            namespace=namespace,
        )
        artifacts = WebLoader(max_tokens=100).load("https://www.griptape.ai")

        vector_store.upsert_text_artifacts(
            {
                namespace: artifacts,
            }
        )

        agent = Agent(tools=[vector_store_tool])

        result = agent.run("Tell me about griptape.")

        assert result.output is not None
        re.search("tape", result.output.to_text(), re.IGNORECASE)
