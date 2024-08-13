from griptape.structures import Pipeline
from griptape.tasks import ToolkitTask
from griptape.tools import TaskMemoryTool, WebScraperTool
from griptape.utils import Stream

pipeline = Pipeline()
pipeline.add_tasks(
    ToolkitTask(
        "Based on https://griptape.ai, tell me what griptape is.",
        tools=[WebScraperTool(off_prompt=True), TaskMemoryTool(off_prompt=False)],
    )
)

for artifact in Stream(pipeline).run():
    print(artifact.value, end="", flush=True)
