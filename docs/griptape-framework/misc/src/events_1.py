from griptape.events import (
    BaseEvent,
    EventListener,
    FinishActionsSubtaskEvent,
    FinishPromptEvent,
    FinishTaskEvent,
    StartActionsSubtaskEvent,
    StartPromptEvent,
    StartTaskEvent,
    event_bus,
)
from griptape.structures import Agent


def handler(event: BaseEvent) -> None:
    print(event.__class__)


event_bus.add_event_listeners(
    [
        EventListener(
            handler,
            event_types=[
                StartTaskEvent,
                FinishTaskEvent,
                StartActionsSubtaskEvent,
                FinishActionsSubtaskEvent,
                StartPromptEvent,
                FinishPromptEvent,
            ],
        )
    ]
)

agent = Agent()

agent.run("tell me about griptape")
