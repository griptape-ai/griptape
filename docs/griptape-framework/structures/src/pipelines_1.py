from griptape.structures import Pipeline
from griptape.tasks import PromptTask

pipeline = Pipeline()

pipeline.add_tasks(
    # take the first argument from the pipeline `run` method
    PromptTask("{{ args[0] }}"),
    # take the output from the previous task and insert it into the prompt
    PromptTask("Say the following like a pirate: {{ parent_output }}"),
)

pipeline.run("Write me a haiku about sailing.")
