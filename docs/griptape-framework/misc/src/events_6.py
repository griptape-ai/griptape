from griptape.events import BaseEvent, EventListener, StartPromptEvent, event_bus
from griptape.structures import Agent

event_bus.add_event_listeners([EventListener(handler=lambda e: print(e), event_types=[StartPromptEvent])])


def handler(event: BaseEvent) -> None:
    if isinstance(event, StartPromptEvent):
        print("Prompt Stack Messages:")
        for message in event.prompt_stack.messages:
            print(f"{message.role}: {message.content}")


agent = Agent()

agent.run("Write me a poem.")
