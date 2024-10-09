from griptape.events import BaseEvent, EventBus, EventListener, StartPromptEvent
from griptape.structures import Agent


def handler(event: BaseEvent) -> None:
    if isinstance(event, StartPromptEvent):
        print("Prompt Stack Messages:")
        for message in event.prompt_stack.messages:
            print(f"{message.role}: {message.to_text()}")


EventBus.add_event_listeners([EventListener(handler=handler, event_types=[StartPromptEvent])])

agent = Agent()

agent.run("Write me a poem.")
