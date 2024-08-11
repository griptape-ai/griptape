from griptape.drivers import GriptapeCloudEventListenerDriver
from griptape.events import EventListener, FinishStructureRunEvent, event_bus
from griptape.structures import Agent

event_bus.add_event_listeners(
    [
        EventListener(
            event_types=[FinishStructureRunEvent],
            # By default, GriptapeCloudEventListenerDriver uses the api key provided
            # in the GT_CLOUD_API_KEY environment variable.
            driver=GriptapeCloudEventListenerDriver(),
        ),
    ]
)

agent = Agent()
agent.run("Create a list of 8 questions for an interview with a science fiction author.")
