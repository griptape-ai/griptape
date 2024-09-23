from griptape.drivers import DuckDuckGoWebSearchDriver
from griptape.structures import Agent
from griptape.tools import PromptSummaryTool, WebSearchTool

agent = Agent(
    tools=[WebSearchTool(web_search_driver=DuckDuckGoWebSearchDriver()), PromptSummaryTool(off_prompt=False)],
)

agent.run("Give me some websites with information about AI frameworks.")
