from griptape.events import EventBus, EventListener, FinishStructureRunEvent, StartPromptEvent
from griptape.structures import Agent

EventBus.add_event_listeners(
    [EventListener(lambda e: print(f"Out of context: {e.type}"), event_types=[StartPromptEvent])]
)

agent = Agent(input="Hello!")

with EventListener(lambda e: print(f"In context: {e.type}"), event_types=[FinishStructureRunEvent]):
    agent.run()

agent.run()
