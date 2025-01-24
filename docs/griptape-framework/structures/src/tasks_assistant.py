import os

from griptape.drivers.assistant.griptape_cloud import GriptapeCloudAssistantDriver
from griptape.structures import Pipeline
from griptape.tasks import AssistantTask

pipeline = Pipeline(
    tasks=[
        AssistantTask(
            assistant_driver=GriptapeCloudAssistantDriver(
                assistant_id=os.environ["GT_CLOUD_ASSISTANT_ID"],
            ),
        ),
    ]
)

pipeline.run("Hello!")
