import logging

from griptape.configs import Defaults
from griptape.events import FinishPromptEvent, FinishStructureRunEvent, TextChunkEvent
from griptape.structures import Agent
from griptape.tools import PromptSummaryTool, WebScraperTool
from griptape.utils import Stream

# Hide Griptape's usual output
logging.getLogger(Defaults.logging_config.logger_name).setLevel(logging.ERROR)

agent = Agent(
    input="Based on https://griptape.ai, tell me what griptape is.",
    tools=[
        PromptSummaryTool(off_prompt=True),
        WebScraperTool(off_prompt=False),
    ],
    stream=True,
)

# Listen for the following event types
event_types = [TextChunkEvent, FinishPromptEvent, FinishStructureRunEvent]

for artifact in Stream(agent, event_types=event_types).run():
    print(artifact.value, end="", flush=True)
