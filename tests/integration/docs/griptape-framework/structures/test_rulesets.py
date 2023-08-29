import re

class TestAgents:
    """
    https://docs.griptape.ai/en/latest/griptape-framework/structures/rulesets/
    """

    def test_rulesets(self):
        from griptape import utils
        from griptape.structures import Agent
        from griptape.rules import Rule, Ruleset

        agent = Agent(
            rulesets=[
                Ruleset(
                    name="Polite customer support agent",
                    rules=[
                        Rule("Behave like a polite customer support agent"),
                        Rule("Act like you work for company SkaterWorld, Inc."),
                        Rule("Discuss only topics related to skateboarding")
                    ]
                )
            ]
        )

        result = agent.run("hi there!")
        assert result.output is not None
        assert re.search('hello', result.output.to_text(), re.IGNORECASE)

        result = agent.run("tell me about griptape")
        assert result.output is not None
        assert re.search('tape', result.output.to_text(), re.IGNORECASE)

        result = agent.run("tell me about sailboats")
        assert result.output is not None
        assert re.search('sorry', result.output.to_text(), re.IGNORECASE)

        assert agent.memory is not None
        result = utils.Conversation(agent.memory)

        assert re.search('hello', str(result), re.IGNORECASE)
        assert re.search('tape', str(result), re.IGNORECASE)
        assert re.search('sorry', str(result), re.IGNORECASE)
