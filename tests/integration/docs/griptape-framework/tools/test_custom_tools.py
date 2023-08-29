class TestCustomTools:
    """
    https://docs.griptape.ai/en/latest/griptape-framework/tools/custom-tools/
    """

    def test_custom_tool(self):
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

        from griptape.structures import Agent

        rng_tool = RandomNumberGenerator()

        agent = Agent(tools=[rng_tool])

        result = agent.run("generate a random number rounded to 5 decimal places")

        assert result.output is not None
