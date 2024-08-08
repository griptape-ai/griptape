from griptape.events import (
    BaseEvent,
    EventListener,
    FinishActionsSubtaskEvent,
    FinishPromptEvent,
    FinishTaskEvent,
    StartActionsSubtaskEvent,
    StartPromptEvent,
    StartTaskEvent,
)
from griptape.structures import Agent


def handler(event: BaseEvent):
    print(event.__class__)


agent = Agent(
    event_listeners=[
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

agent.run("tell me about griptape")
