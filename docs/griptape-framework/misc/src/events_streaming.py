from griptape.events import BaseEvent
from griptape.structures import Agent

agent = Agent()

for event in agent.run_stream("Hi!", event_types=[BaseEvent]):  # All Events
    print(type(event))
