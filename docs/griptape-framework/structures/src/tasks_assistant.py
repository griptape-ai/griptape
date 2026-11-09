import os

from griptape.drivers.assistant.openai import OpenAiAssistantDriver
from griptape.structures import Pipeline
from griptape.tasks import AssistantTask

pipeline = Pipeline(
    tasks=[
        AssistantTask(
            assistant_driver=OpenAiAssistantDriver(
                assistant_id=os.environ["OPENAI_ASSISTANT_ID"],
            ),
        ),
    ]
)

pipeline.run("Hello!")
