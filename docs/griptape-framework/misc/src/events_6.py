from griptape.events import BaseEvent, EventBus, EventListener, StartPromptEvent
from griptape.structures import Agent

EventBus.add_event_listeners([EventListener(handler=lambda e: print(e), event_types=[StartPromptEvent])])


def handler(event: BaseEvent) -> None:
    if isinstance(event, StartPromptEvent):
        print("Prompt Stack Messages:")
        for message in event.prompt_stack.messages:
            print(f"{message.role}: {message.content}")


agent = Agent()

agent.run("Write me a poem.")
