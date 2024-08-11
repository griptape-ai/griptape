from griptape.events import BaseEvent, EventListener, event_bus
from griptape.structures import Agent


def handler1(event: BaseEvent) -> None:
    print("Handler 1", event.__class__)


def handler2(event: BaseEvent) -> None:
    print("Handler 2", event.__class__)


event_bus.add_event_listeners(
    [
        EventListener(handler1),
        EventListener(handler2),
    ]
)

agent = Agent()

agent.run("tell me about griptape")
