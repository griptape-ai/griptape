import os

from griptape.configs import Defaults
from griptape.configs.drivers import DriversConfig
from griptape.drivers import AwsIotCoreEventListenerDriver, OpenAiChatPromptDriver
from griptape.events import EventBus, EventListener, FinishStructureRunEvent
from griptape.rules import Rule
from griptape.structures import Agent

Defaults.drivers_config = DriversConfig(prompt_driver=OpenAiChatPromptDriver(model="gpt-3.5-turbo", temperature=0.7))
EventBus.add_event_listeners(
    [
        EventListener(
            event_types=[FinishStructureRunEvent],
            event_listener_driver=AwsIotCoreEventListenerDriver(
                topic=os.environ["AWS_IOT_CORE_TOPIC"],
                iot_endpoint=os.environ["AWS_IOT_CORE_ENDPOINT"],
            ),
        ),
    ]
)

agent = Agent(
    rules=[Rule(value="You will be provided with a text, and your task is to extract the airport codes from it.")],
)

agent.run("I want to fly from Orlando to Boston")
