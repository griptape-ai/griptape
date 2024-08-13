from griptape.structures import Agent
from griptape.tools import QueryTool, WebScraperTool

agent = Agent(tools=[WebScraperTool(off_prompt=True), QueryTool()])

agent.run("Tell me about the architecture as described here: https://neovim.io/doc/user/vim_diff.html")
