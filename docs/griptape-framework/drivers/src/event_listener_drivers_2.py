from griptape.artifacts import TextArtifact
from griptape.drivers import GriptapeCloudEventListenerDriver
from griptape.events import FinishStructureRunEvent

# By default, GriptapeCloudEventListenerDriver uses the api key provided
# in the GT_CLOUD_API_KEY environment variable.
event_driver = GriptapeCloudEventListenerDriver()

done_event = FinishStructureRunEvent(
    output_task_input=TextArtifact("Just started!"),
    output_task_output=TextArtifact("All done!"),
)

event_driver.publish_event(done_event)
