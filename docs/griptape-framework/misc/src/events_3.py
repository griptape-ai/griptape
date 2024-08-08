from typing import cast

from griptape.config import OpenAiStructureConfig
from griptape.drivers import OpenAiChatPromptDriver
from griptape.events import CompletionChunkEvent, EventListener, event_bus
from griptape.structures import Pipeline
from griptape.tasks import ToolkitTask
from griptape.tools import TaskMemoryClient, WebScraper

event_bus.add_event_listeners(
    [
        EventListener(
            lambda e: print(cast(CompletionChunkEvent, e).token, end="", flush=True),
            event_types=[CompletionChunkEvent],
        )
    ]
)

pipeline = Pipeline(
    config=OpenAiStructureConfig(prompt_driver=OpenAiChatPromptDriver(model="gpt-4o", stream=True)),
)

pipeline.add_tasks(
    ToolkitTask(
        "Based on https://griptape.ai, tell me what griptape is.",
        tools=[WebScraper(off_prompt=True), TaskMemoryClient(off_prompt=False)],
    )
)

pipeline.run()
