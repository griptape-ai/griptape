from griptape.structures import Agent
from griptape.tasks import ToolkitTask
from griptape.tools import FileManager, PromptSummaryTool, WebScraper

agent = Agent()
agent.add_task(
    ToolkitTask(
        "Load https://www.griptape.ai, summarize it, and store it in a file called griptape.txt",
        tools=[WebScraper(off_prompt=True), FileManager(off_prompt=True), PromptSummaryTool(off_prompt=True)],
    ),
)

agent.run()
