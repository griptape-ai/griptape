from griptape import utils
from griptape.events import BaseEvent, EventBus, EventListener, FinishPromptEvent
from griptape.structures import Agent

token_counter = utils.TokenCounter()


def count_tokens(e: BaseEvent) -> None:
    if isinstance(e, FinishPromptEvent) and e.output_token_count is not None:
        token_counter.add_tokens(e.output_token_count)


EventBus.add_event_listeners(
    [
        EventListener(
            count_tokens,
            event_types=[FinishPromptEvent],
        )
    ]
)


agent = Agent()

agent.run("tell me about large language models")

print(f"total tokens: {token_counter.tokens}")
