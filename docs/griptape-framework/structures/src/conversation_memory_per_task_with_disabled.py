from griptape.structures import Pipeline
from griptape.tasks import PromptTask

pipeline = Pipeline(
    conversation_memory_strategy=Pipeline.ConversationMemoryStrategy.PER_TASK,
    tasks=[
        PromptTask("Respond to this request: {{ args[0] }}", id="input"),
        PromptTask("Improve the writing of this: {{ parent_output }}", id="improve", conversation_memory=None),
        PromptTask("Respond as a pirate", id="output"),
    ],
)

pipeline.run("My favorite animal is a Liger.")

if pipeline.conversation_memory is not None:
    for run in pipeline.conversation_memory.runs:
        print("Input", run.input.value)
        print("Output", run.output.value)
        print("\n\n")
