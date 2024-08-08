import os

from griptape.drivers import PusherEventListenerDriver
from griptape.events import EventListener, FinishStructureRunEvent, event_bus
from griptape.structures import Agent

event_bus.add_event_listeners(
    [
        EventListener(
            event_types=[FinishStructureRunEvent],
            driver=PusherEventListenerDriver(
                batched=False,
                app_id=os.environ["PUSHER_APP_ID"],
                key=os.environ["PUSHER_KEY"],
                secret=os.environ["PUSHER_SECRET"],
                cluster=os.environ["PUSHER_CLUSTER"],
                channel="my-channel",
                event_name="my-event",
            ),
        ),
    ],
)

agent = Agent()

agent.run("Analyze the pros and cons of remote work vs. office work")
