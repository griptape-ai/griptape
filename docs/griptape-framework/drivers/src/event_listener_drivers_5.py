from griptape.drivers.event_listener.griptape_cloud import GriptapeCloudEventListenerDriver
from griptape.events import EventBus, EventListener, FinishStructureRunEvent
from griptape.structures import Agent

EventBus.add_event_listeners(
    [
        EventListener(
            event_types=[FinishStructureRunEvent],
            # By default, GriptapeCloudEventListenerDriver uses the api key provided
            # in the GT_CLOUD_API_KEY environment variable.
            event_listener_driver=GriptapeCloudEventListenerDriver(),
        ),
    ]
)

agent = Agent()
agent.run("Create a list of 8 questions for an interview with a science fiction author.")
