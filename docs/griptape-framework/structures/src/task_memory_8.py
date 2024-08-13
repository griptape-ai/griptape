from griptape.structures import Agent
from griptape.tools import PromptSummaryTool, WebScraperTool

agent = Agent(
    tools=[
        WebScraperTool(off_prompt=True),  # This tool will store the data in Task Memory
        PromptSummaryTool(
            off_prompt=True
        ),  # This tool will store the data back in Task Memory with no way to get it out
    ]
)
agent.run(
    "According to this page https://en.wikipedia.org/wiki/Dark_forest_hypothesis, what is the Dark Forest Hypothesis?"
)
