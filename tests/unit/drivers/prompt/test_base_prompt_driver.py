from griptape.events import FinishPromptEvent, StartPromptEvent
from griptape.utils import PromptStack
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_failing_prompt_driver import MockFailingPromptDriver
from griptape.artifacts import ErrorArtifact, TextArtifact
from griptape.tasks import PromptTask
from griptape.structures import Pipeline


class TestBasePromptDriver:
    def test_run_via_pipeline_retries_success(self):
        driver = MockPromptDriver(max_attempts=1)
        pipeline = Pipeline(prompt_driver=driver)

        pipeline.add_task(PromptTask("test"))

        assert isinstance(pipeline.run().output_task.output, TextArtifact)

    def test_run_via_pipeline_retries_failure(self):
        driver = MockFailingPromptDriver(max_failures=2, max_attempts=1)
        pipeline = Pipeline(prompt_driver=driver)

        pipeline.add_task(PromptTask("test"))

        assert isinstance(pipeline.run().output_task.output, ErrorArtifact)

    def test_run_via_pipeline_publishes_events(self, mocker):
        mock_publish_event = mocker.patch.object(Pipeline, "publish_event")
        driver = MockPromptDriver()
        pipeline = Pipeline(prompt_driver=driver)
        pipeline.add_task(PromptTask("test"))

        pipeline.run()

        events = [call_args[0][0] for call_args in mock_publish_event.call_args_list]
        assert instance_count(events, StartPromptEvent) == 1
        assert instance_count(events, FinishPromptEvent) == 1

    def test_run(self):
        assert isinstance(MockPromptDriver().run(PromptStack(inputs=[])), TextArtifact)


def instance_count(instances, clazz):
    return len([instance for instance in instances if isinstance(instance, clazz)])
