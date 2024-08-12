from griptape.structures import Agent
from griptape.tools import QueryClient, WebScraper

agent = Agent(tools=[WebScraper(off_prompt=True), QueryClient()])

agent.run("Tell me about the architecture as described here: https://neovim.io/doc/user/vim_diff.html")
