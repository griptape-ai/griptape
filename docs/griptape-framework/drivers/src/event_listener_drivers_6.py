import os

from griptape.drivers.event_listener.webhook import WebhookEventListenerDriver
from griptape.events import EventBus, EventListener, FinishStructureRunEvent
from griptape.structures import Agent

EventBus.add_event_listeners(
    [
        EventListener(
            event_types=[FinishStructureRunEvent],
            event_listener_driver=WebhookEventListenerDriver(
                webhook_url=os.environ["WEBHOOK_URL"],
            ),
        ),
    ]
)

agent = Agent()

agent.run("Analyze the pros and cons of remote work vs. office work")
