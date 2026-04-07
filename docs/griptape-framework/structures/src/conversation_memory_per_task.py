from griptape.structures import Pipeline
from griptape.tasks import PromptTask

pipeline = Pipeline(
    conversation_memory_strategy="per_task",
    tasks=[
        PromptTask("Respond to this request: {{ args[0] }}", id="input"),
        PromptTask("Improve the writing", id="improve"),
        PromptTask("Respond as a pirate", id="output"),
    ],
)

pipeline.run("My favorite animal is a Liger.")

if pipeline.conversation_memory is not None:
    for run in pipeline.conversation_memory.runs:
        print("Input", run.input.value)
        print("Output", run.output.value)
        print("\n\n")
