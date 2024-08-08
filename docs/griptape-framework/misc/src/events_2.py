from griptape.events import BaseEvent, EventListener
from griptape.structures import Agent


def handler1(event: BaseEvent):
    print("Handler 1", event.__class__)


def handler2(event: BaseEvent):
    print("Handler 2", event.__class__)


agent = Agent(
    event_listeners=[
        EventListener(handler1),
        EventListener(handler2),
    ]
)

agent.run("tell me about griptape")
