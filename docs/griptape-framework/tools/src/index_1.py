from griptape.structures import Pipeline
from griptape.tasks import ToolkitTask
from griptape.tools import FileManager, PromptSummaryTool, WebScraper

pipeline = Pipeline()

pipeline.add_tasks(
    ToolkitTask(
        "Load https://www.griptape.ai, summarize it, and store it in a file called griptape.txt",
        tools=[
            WebScraper(off_prompt=True),
            FileManager(off_prompt=True),
            PromptSummaryTool(off_prompt=False),
        ],
    ),
)

pipeline.run()
