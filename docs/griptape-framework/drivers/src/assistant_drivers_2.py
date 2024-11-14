import os

from griptape.drivers import OpenAiAssistantDriver
from griptape.structures import Pipeline
from griptape.tasks import AssistantTask
from griptape.utils.stream import Stream

pipeline = Pipeline(
    tasks=[
        AssistantTask(
            driver=OpenAiAssistantDriver(
                assistant_id=os.environ["OPENAI_ASSISTANT_ID"], thread_id=os.environ["OPENAI_THREAD_ID"]
            ),
        ),
    ]
)

for chunk in Stream(pipeline).run("I need to solve the equation `3x + 11 = 14`. Can you help me?"):
    print(chunk, end="", flush=True)
