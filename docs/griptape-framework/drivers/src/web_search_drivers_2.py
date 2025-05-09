import os

from griptape.drivers.web_search.google import GoogleWebSearchDriver
from griptape.structures import Agent
from griptape.tools import PromptSummaryTool, WebSearchTool

agent = Agent(
    tools=[
        WebSearchTool(
            web_search_driver=GoogleWebSearchDriver(
                api_key=os.environ["GOOGLE_API_KEY"],
                search_id=os.environ["GOOGLE_API_SEARCH_ID"],
            ),
        ),
        PromptSummaryTool(off_prompt=False),
    ],
)
agent.run("Give me some websites with information about AI frameworks.")
