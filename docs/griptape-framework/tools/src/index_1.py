from griptape.structures import Pipeline
from griptape.tasks import PromptTask
from griptape.tools import FileManagerTool, PromptSummaryTool, WebScraperTool

pipeline = Pipeline()

pipeline.add_tasks(
    PromptTask(
        "Load https://www.griptape.ai, summarize it, and store it in a file called griptape.txt",
        tools=[
            WebScraperTool(off_prompt=True),
            FileManagerTool(off_prompt=True),
            PromptSummaryTool(off_prompt=False),
        ],
    ),
)

pipeline.run()
