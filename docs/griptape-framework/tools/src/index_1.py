from griptape.structures import Pipeline
from griptape.tasks import ToolkitTask
from griptape.tools import FileManagerTool, TaskMemoryTool, WebScraperTool

pipeline = Pipeline()

pipeline.add_tasks(
    ToolkitTask(
        "Load https://www.griptape.ai, summarize it, and store it in a file called griptape.txt",
        tools=[WebScraperTool(off_prompt=True), FileManagerTool(off_prompt=True), TaskMemoryTool(off_prompt=False)],
    ),
)

pipeline.run()
