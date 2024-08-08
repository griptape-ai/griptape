import os

from griptape.drivers import WebhookEventListenerDriver
from griptape.events import (
    EventListener,
    FinishStructureRunEvent,
)
from griptape.structures import Agent

agent = Agent(
    event_listeners=[
        EventListener(
            event_types=[FinishStructureRunEvent],
            driver=WebhookEventListenerDriver(
                webhook_url=os.environ["WEBHOOK_URL"],
            ),
        ),
    ],
)

agent.run("Analyze the pros and cons of remote work vs. office work")
