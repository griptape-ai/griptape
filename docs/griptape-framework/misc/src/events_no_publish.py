from __future__ import annotations

from typing import Optional

from griptape.artifacts import ErrorArtifact, InfoArtifact
from griptape.drivers import GriptapeCloudEventListenerDriver
from griptape.events import BaseEvent, EventBus, EventListener, FinishStructureRunEvent
from griptape.structures import Agent


def handler_maybe_drop_events(event: FinishStructureRunEvent) -> Optional[BaseEvent | dict]:
    if event.structure_id == "some_structure_id":
        # Drop the event if the structure_id is "some_structure_id"
        return None
    if isinstance(event.output_task_output, InfoArtifact):
        # Print the output of the task if it is an InfoArtifact
        # and then drop the event
        print(f"Info: {event.output_task_output}")
        return None
    if isinstance(event.output_task_output, ErrorArtifact):
        # Print the output of the task if it is an ErrorArtifact
        # and then convert it to a dictionary and return it
        print(f"Error: {event.output_task_output}")
        return {
            "error": event.output_task_output.to_text(),
            "exception_message": str(event.output_task_output.exception),
        }

    return event


EventBus.add_event_listeners(
    [
        EventListener(
            handler_maybe_drop_events,  # pyright: ignore[reportArgumentType]
            event_types=[FinishStructureRunEvent],
            # By default, GriptapeCloudEventListenerDriver uses the api key provided
            # in the GT_CLOUD_API_KEY environment variable.
            event_listener_driver=GriptapeCloudEventListenerDriver(),
        ),
    ]
)


agent1 = Agent(id="some_structure_id")
agent1.run("Create a list of 8 questions for an interview with a science fiction author.")

agent2 = Agent(id="another_structure_id")
agent2.run("Create a list of 10 questions for an interview with a theoretical physicist.")
