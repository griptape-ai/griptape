import os

from griptape.drivers import WebhookEventListenerDriver
from griptape.events import EventBus, EventListener, FinishStructureRunEvent
from griptape.structures import Agent

EventBus.add_event_listeners(
    [
        EventListener(
            event_types=[FinishStructureRunEvent],
            driver=WebhookEventListenerDriver(
                webhook_url=os.environ["WEBHOOK_URL"],
            ),
        ),
    ]
)

agent = Agent()

agent.run("Analyze the pros and cons of remote work vs. office work")
