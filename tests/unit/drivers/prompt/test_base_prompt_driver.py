import json
import warnings

import pytest

from griptape.artifacts import ActionArtifact, ErrorArtifact, TextArtifact
from griptape.common import Message, PromptStack
from griptape.events import FinishPromptEvent, StartPromptEvent
from griptape.events.event_bus import _EventBus
from griptape.structures import Pipeline
from griptape.tasks import PromptTask
from griptape.tools.structured_output.tool import StructuredOutputTool
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

    def test_native_structured_output_strategy(self):
        from schema import Schema

        prompt_driver = MockPromptDriver(
            mock_structured_output={"baz": "foo"},
            structured_output_strategy="native",
        )

        output_schema = Schema({"baz": str})
        output = prompt_driver.run(PromptStack(messages=[], output_schema=output_schema)).to_artifact()

        assert isinstance(output, TextArtifact)
        assert output.value == json.dumps({"baz": "foo"})

    def test_tool_structured_output_strategy(self):
        from schema import Schema

        output_schema = Schema({"baz": str})
        prompt_driver = MockPromptDriver(
            mock_structured_output={"baz": "foo"},
            structured_output_strategy="tool",
            use_native_tools=True,
        )
        prompt_stack = PromptStack(messages=[], output_schema=output_schema)
        output = prompt_driver.run(prompt_stack).to_artifact()
        output = prompt_driver.run(prompt_stack).to_artifact()

        assert isinstance(output, ActionArtifact)
        assert isinstance(prompt_stack.tools[0], StructuredOutputTool)
        assert prompt_stack.tools[0].output_schema == output_schema
        assert output.value.input == {"values": {"baz": "foo"}}

    def test_rule_structured_output_strategy_empty(self):
        from schema import Schema

        output_schema = Schema({"baz": str})
        prompt_driver = MockPromptDriver(
            mock_structured_output={"baz": "foo"},
            structured_output_strategy="rule",
        )
        prompt_stack = PromptStack(messages=[], output_schema=output_schema)
        output = prompt_driver.run(prompt_stack).to_artifact()

        assert len(prompt_stack.system_messages) == 1
        assert prompt_stack.messages[0].is_system()
        assert "baz" in prompt_stack.messages[0].content[0].to_text()
        assert isinstance(output, TextArtifact)
        assert output.value == json.dumps({"baz": "foo"})

    def test_rule_structured_output_strategy_populated(self):
        from schema import Schema

        output_schema = Schema({"baz": str})
        prompt_driver = MockPromptDriver(
            mock_structured_output={"baz": "foo"},
            structured_output_strategy="rule",
        )
        prompt_stack = PromptStack(
            messages=[
                Message(content="foo", role=Message.SYSTEM_ROLE),
            ],
            output_schema=output_schema,
        )
        output = prompt_driver.run(prompt_stack).to_artifact()
        assert len(prompt_stack.system_messages) == 1
        assert prompt_stack.messages[0].is_system()
        assert prompt_stack.messages[0].content[1].to_text() == "\n\n"
        assert "baz" in prompt_stack.messages[0].content[2].to_text()
        assert isinstance(output, TextArtifact)
        assert output.value == json.dumps({"baz": "foo"})

    def test_deprecated_import(self):
        with pytest.warns(DeprecationWarning):
            from griptape.drivers import BasePromptDriver

            assert BasePromptDriver

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            from griptape.drivers.prompt.base_prompt_driver import BasePromptDriver

            assert BasePromptDriver
