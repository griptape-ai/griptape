from griptape.structures import Agent
from griptape.tools import PromptSummaryClient, WebScraper

agent = Agent(tools=[WebScraper(off_prompt=True), PromptSummaryClient()])

agent.run(
    "How can I build Neovim from source for MacOS according to this https://github.com/neovim/neovim/blob/master/BUILD.md"
)
