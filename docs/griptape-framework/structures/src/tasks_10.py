from griptape.artifacts import BaseArtifact, TextArtifact
from griptape.structures import Pipeline
from griptape.tasks import CodeExecutionTask, PromptTask


def character_counter(task: CodeExecutionTask) -> BaseArtifact:
    result = len(task.input)
    # For functions that don't need to return anything, we recommend returning task.input
    return TextArtifact(str(result))


# Instantiate the pipeline
pipeline = Pipeline()

pipeline.add_tasks(
    # take the first argument from the pipeline `run` method
    CodeExecutionTask(run_fn=character_counter),
    # # take the output from the previous task and insert it into the prompt
    PromptTask("{{args[0]}} using {{ parent_output }} characters"),
)

pipeline.run("Write me a line in a poem")
