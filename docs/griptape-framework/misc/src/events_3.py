from griptape.drivers import OpenAiChatPromptDriver
from griptape.events import BaseChunkEvent, EventBus, EventListener
from griptape.structures import Pipeline
from griptape.tasks import ToolkitTask
from griptape.tools import PromptSummaryTool, WebScraperTool

EventBus.add_event_listeners(
    [
        EventListener(
            lambda e: print(str(e), end="", flush=True),
            event_types=[BaseChunkEvent],
        ),
    ]
)

pipeline = Pipeline()
pipeline.add_tasks(
    ToolkitTask(
        "Based on https://griptape.ai, tell me what griptape is.",
        prompt_driver=OpenAiChatPromptDriver(model="gpt-4o", stream=True),
        tools=[WebScraperTool(off_prompt=True), PromptSummaryTool(off_prompt=False)],
    )
)

pipeline.run()
