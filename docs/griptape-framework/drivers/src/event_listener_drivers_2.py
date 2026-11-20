import os

from griptape.artifacts import TextArtifact
from griptape.drivers.event_listener.webhook import WebhookEventListenerDriver
from griptape.events import FinishStructureRunEvent

event_driver = WebhookEventListenerDriver(
    webhook_url=os.environ["WEBHOOK_URL"],
)

done_event = FinishStructureRunEvent(
    output_task_input=TextArtifact("Just started!"),
    output_task_output=TextArtifact("All done!"),
)

event_driver.publish_event(done_event)
