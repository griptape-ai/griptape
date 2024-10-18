from griptape.drivers import OpenAiChatPromptDriver
from griptape.events import ActionChunkEvent, EventBus, EventListener, TextChunkEvent
from griptape.structures import Pipeline
from griptape.tasks import ToolkitTask
from griptape.tools import PromptSummaryTool, WebScraperTool


def action_chunk_listener(event: ActionChunkEvent) -> None:
    if event.tag is not None and event.name is not None and event.path is not None:
        print(f"{event.name}.{event.tag} ({event.path}) ", end="", flush=True)
    if event.partial_input is not None:
        print(event.partial_input, end="", flush=True)


EventBus.add_event_listeners(
    [
        EventListener(
            lambda e: print(e.token, end="", flush=True),
            event_types=[TextChunkEvent],
        ),
        EventListener(
            action_chunk_listener,
            event_types=[ActionChunkEvent],
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
