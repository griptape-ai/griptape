from griptape.memory.structure import ConversationMemory
from griptape.structures import Pipeline
from griptape.tasks import PromptTask, ToolkitTask
from griptape.tools import FileManager, TaskMemoryClient, WebScraper

# Pipelines represent sequences of tasks.
pipeline = Pipeline(conversation_memory=ConversationMemory())

pipeline.add_tasks(
    # Load up the first argument from `pipeline.run`.
    ToolkitTask(
        "{{ args[0] }}",
        # Add tools for web scraping, and file management
        tools=[WebScraper(off_prompt=True), FileManager(off_prompt=True), TaskMemoryClient(off_prompt=False)],
    ),
    # Augment `input` from the previous task.
    PromptTask("Say the following in spanish: {{ parent_output }}"),
)

pipeline.run("Load https://www.griptape.ai, summarize it, and store it in griptape.txt")
