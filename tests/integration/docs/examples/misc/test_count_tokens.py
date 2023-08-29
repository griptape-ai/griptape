class TestCountTokens:
    """
    https://docs.griptape.ai/en/latest/examples/count-tokens/
    """
    def test_count_tokens(self):
        from griptape import utils
        from griptape.events import (
            StartPromptEvent,
            FinishPromptEvent,
        )
        from griptape.structures import Agent

        token_counter = utils.TokenCounter()

        agent = Agent(
            event_listeners={
                StartPromptEvent: [lambda e: token_counter.add_tokens(e.token_count)],
                FinishPromptEvent: [lambda e: token_counter.add_tokens(e.token_count)],
            }
        )

        agent.run("tell me about large language models")
        agent.run("tell me about GPT")

        print(f"total tokens: {token_counter.tokens}")
        assert token_counter.tokens != 0 
