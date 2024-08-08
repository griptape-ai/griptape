from griptape.artifacts import ErrorArtifact, TextArtifact
from griptape.common import Message, PromptStack
from griptape.events import FinishPromptEvent, StartPromptEvent
from griptape.events.event_bus import _EventBus
from griptape.structures import Pipeline
from griptape.tasks import PromptTask, ToolkitTask
from tests.mocks.mock_failing_prompt_driver import MockFailingPromptDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_tool.tool import MockTool


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
        mock_publish_event = mocker.patch.object(_EventBus, "publish_event")
        driver = MockPromptDriver()
        pipeline = Pipeline(prompt_driver=driver)
        pipeline.add_task(PromptTask("test"))

        pipeline.run()

        events = [call_args[0][0] for call_args in mock_publish_event.call_args_list]
        assert len([instance for instance in events if isinstance(instance, StartPromptEvent)]) == 1
        assert len([instance for instance in events if isinstance(instance, FinishPromptEvent)]) == 1

    def test_run(self):
        assert isinstance(MockPromptDriver().run(PromptStack(messages=[])), Message)

    def test_run_with_stream(self):
        result = MockPromptDriver(stream=True).run(PromptStack(messages=[]))
        assert isinstance(result, Message)
        assert result.value == "mock output"

    def test_run_with_tools(self):
        driver = MockPromptDriver(max_attempts=1, use_native_tools=True)
        pipeline = Pipeline(prompt_driver=driver)

        pipeline.add_task(ToolkitTask(tools=[MockTool()]))

        output = pipeline.run().output_task.output
        assert isinstance(output, TextArtifact)
        assert output.value == "mock output"

    def test_run_with_tools_and_stream(self):
        driver = MockPromptDriver(max_attempts=1, stream=True, use_native_tools=True)
        pipeline = Pipeline(prompt_driver=driver)

        pipeline.add_task(ToolkitTask(tools=[MockTool()]))

        output = pipeline.run().output_task.output
        assert isinstance(output, TextArtifact)
        assert output.value == "mock output"
