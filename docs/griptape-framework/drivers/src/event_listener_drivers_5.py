from griptape.drivers import GriptapeCloudEventListenerDriver
from griptape.events import (
    EventListener,
    FinishStructureRunEvent,
)
from griptape.structures import Agent

agent = Agent(
    event_listeners=[
        EventListener(
            event_types=[FinishStructureRunEvent],
            # By default, GriptapeCloudEventListenerDriver uses the api key provided
            # in the GT_CLOUD_API_KEY environment variable.
            driver=GriptapeCloudEventListenerDriver(),
        ),
    ],
)

agent.run("Create a list of 8 questions for an interview with a science fiction author.")
