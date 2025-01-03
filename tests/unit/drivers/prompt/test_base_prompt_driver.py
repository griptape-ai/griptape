import pytest

from griptape.artifacts import ErrorArtifact, TextArtifact
from griptape.common import Message, PromptStack
from griptape.events import FinishPromptEvent, StartPromptEvent
from griptape.events.event_bus import _EventBus
from griptape.structures import Pipeline
from griptape.tasks import PromptTask
from tests.mocks.mock_failing_prompt_driver import MockFailingPromptDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_tool.tool import MockTool


class TestBasePromptDriver:
    def test_run_via_pipeline_retries_success(self, mock_config):
        mock_config.drivers_config.prompt_driver = MockPromptDriver(max_attempts=2)
        pipeline = Pipeline()

        pipeline.add_task(PromptTask("test"))

        assert isinstance(pipeline.run().output_task.output, TextArtifact)

    def test_run_via_pipeline_retries_failure(self, mock_config):
        mock_config.drivers_config.prompt_driver = MockFailingPromptDriver(max_failures=2, max_attempts=1)
        pipeline = Pipeline()

        pipeline.add_task(PromptTask("test"))

        assert isinstance(pipeline.run().output_task.output, ErrorArtifact)

    def test_run_via_pipeline_publishes_events(self, mocker):
        mock_publish_event = mocker.patch.object(_EventBus, "publish_event")
        pipeline = Pipeline()
        pipeline.add_task(PromptTask("test"))

        pipeline.run()

        events = [call_args[0][0] for call_args in mock_publish_event.call_args_list]
        assert len([instance for instance in events if isinstance(instance, StartPromptEvent)]) == 1
        assert len([instance for instance in events if isinstance(instance, FinishPromptEvent)]) == 1

    def test_run(self):
        assert isinstance(MockPromptDriver().run(PromptStack(messages=[])), Message)
        assert isinstance(MockPromptDriver().run(TextArtifact("")), Message)

    def test_run_with_stream(self):
        result = MockPromptDriver(stream=True).run(PromptStack(messages=[]))
        assert isinstance(result, Message)
        assert result.value == "mock output"

    def test_run_with_tools(self, mock_config):
        mock_config.drivers_config.prompt_driver = MockPromptDriver(max_attempts=1, use_native_tools=True)
        pipeline = Pipeline()

        pipeline.add_task(PromptTask(tools=[MockTool()]))

        output = pipeline.run().output_task.output
        assert isinstance(output, TextArtifact)
        assert output.value == "mock output"

    def test_run_with_tools_and_stream(self, mock_config):
        mock_config.driver = MockPromptDriver(max_attempts=1, stream=True, use_native_tools=True)
        pipeline = Pipeline()

        pipeline.add_task(PromptTask(tools=[MockTool()]))

        output = pipeline.run().output_task.output
        assert isinstance(output, TextArtifact)
        assert output.value == "mock output"

    def test__add_structured_output_tool(self):
        from schema import Schema

        from griptape.tools.structured_output.tool import StructuredOutputTool

        mock_prompt_driver = MockPromptDriver()

        prompt_stack = PromptStack()

        with pytest.raises(ValueError, match="PromptStack must have an output schema to use structured output."):
            mock_prompt_driver._add_structured_output_tool_if_absent(prompt_stack)

        prompt_stack.output_schema = Schema({"foo": str})

        mock_prompt_driver._add_structured_output_tool_if_absent(prompt_stack)
        # Ensure it doesn't get added twice
        mock_prompt_driver._add_structured_output_tool_if_absent(prompt_stack)
        assert len(prompt_stack.tools) == 1
        assert isinstance(prompt_stack.tools[0], StructuredOutputTool)
        assert prompt_stack.tools[0].output_schema is prompt_stack.output_schema
