from griptape.structures import Agent
from griptape.tools import PromptSummaryTool, WebScraper

agent = Agent(tools=[WebScraper(off_prompt=True), PromptSummaryTool(off_prompt=False)])

agent.run("Based on https://www.griptape.ai/, tell me what griptape is")
