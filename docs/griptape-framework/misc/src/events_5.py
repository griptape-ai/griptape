from griptape import utils
from griptape.events import BaseEvent, EventListener, FinishPromptEvent, StartPromptEvent
from griptape.structures import Agent

token_counter = utils.TokenCounter()


def count_tokens(e: BaseEvent) -> None:
    if isinstance(e, FinishPromptEvent) and e.output_token_count is not None:
        token_counter.add_tokens(e.output_token_count)


agent = Agent(
    event_listeners=[
        EventListener(
            handler=lambda e: count_tokens(e),
            event_types=[StartPromptEvent, FinishPromptEvent],
        )
    ]
)

agent.run("tell me about large language models")

print(f"total tokens: {token_counter.tokens}")
