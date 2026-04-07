import os

from griptape.drivers.assistant.griptape_cloud import GriptapeCloudAssistantDriver
from griptape.structures import Pipeline
from griptape.tasks import AssistantTask
from griptape.utils.stream import Stream

pipeline = Pipeline(
    tasks=[
        AssistantTask(
            assistant_driver=GriptapeCloudAssistantDriver(
                assistant_id=os.environ["GT_CLOUD_ASSISTANT_ID"],
                stream=True,
            ),
        ),
    ]
)

for chunk in Stream(pipeline).run("Write me long poem"):
    print(chunk, end="", flush=True)
