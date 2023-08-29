import re


class TestTalkToAWebpage:
    """
    https://docs.griptape.ai/en/latest/examples/talk-to-a-webpage/
    """

    def test_talk_to_a_webpage(self):
        from griptape.engines import VectorQueryEngine
        from griptape.loaders import WebLoader
        from griptape.rules import Ruleset, Rule
        from griptape.structures import Agent
        from griptape.tools import VectorStoreClient

        namespace = "physics-wiki"

        engine = VectorQueryEngine()

        artifacts = WebLoader().load("https://en.wikipedia.org/wiki/Physics")

        engine.vector_store_driver.upsert_text_artifacts({namespace: artifacts})

        vector_store_tool = VectorStoreClient(
            description="Contains information about physics. "
            "Use it to answer any physics-related questions.",
            query_engine=engine,
            namespace=namespace,
        )

        agent = Agent(
            rulesets=[
                Ruleset(
                    name="Physics Tutor",
                    rules=[
                        Rule("Always introduce yourself as a physics tutor"),
                        Rule("Be truthful. Only discuss physics."),
                    ],
                )
            ],
            tools=[vector_store_tool],
        )

        result = agent.run("Tell me about gravity")

        assert result.output is not None
        assert re.search("gravity", result.output.to_text(), re.IGNORECASE)
