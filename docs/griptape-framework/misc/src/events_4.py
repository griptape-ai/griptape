import logging

from griptape.config import config
from griptape.structures import Agent
from griptape.tools import PromptSummaryTool, WebScraperTool
from griptape.utils import Stream

# Hide Griptape's usual output
logging.getLogger(config.logging_config.logger_name).setLevel(logging.ERROR)

agent = Agent(
    input="Based on https://griptape.ai, tell me what griptape is.",
    tools=[
        PromptSummaryTool(off_prompt=True),
        WebScraperTool(off_prompt=False),
    ],
    stream=True,
)


for artifact in Stream(agent).run():
    print(artifact.value, end="", flush=True)
