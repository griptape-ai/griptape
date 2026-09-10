import importlib
import json
import re
import warnings

import pytest

from griptape.artifacts import ActionArtifact, ErrorArtifact, TextArtifact
from griptape.common import AudioMessageContent, DeltaMessage, Message, PromptStack, TextMessageContent
from griptape.events import FinishPromptEvent, StartPromptEvent
from griptape.events.event_bus import _EventBus
from griptape.structures import Pipeline
from griptape.tasks import PromptTask
from griptape.tools.structured_output.tool import StructuredOutputTool
from tests.mocks.mock_failing_prompt_driver import MockFailingPromptDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_stream_usage_prompt_driver import MockStreamUsagePromptDriver
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

    @pytest.mark.parametrize("stream", [True, False])
    @pytest.mark.parametrize("use_native_tools", [True, False])
    @pytest.mark.parametrize("modalities", [["text"], ["text", "audio"]])
    @pytest.mark.parametrize("tools", [[], [MockTool()]])
    def test_run(self, use_native_tools, stream, modalities, tools):
        driver = MockPromptDriver(
            stream=stream, use_native_tools=use_native_tools, modalities=modalities, max_attempts=1
        )

        result = driver.run(PromptStack(tools=tools))

        assert isinstance(result, Message)
        if use_native_tools and tools:
            assert result.value.input == {"test": "test-value"}
        else:
            if "text" in modalities:
                assert result.has_any_content_type(TextMessageContent)
            if "audio" in modalities:
                assert result.has_any_content_type(AudioMessageContent)

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
        assert output.value.input == {"baz": "foo"}

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
        with pytest.warns(DeprecationWarning, match=r"Importing from `griptape\.drivers` is deprecated"):
            from griptape.drivers import BasePromptDriver

        assert BasePromptDriver

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            from griptape.drivers.prompt.base_prompt_driver import BasePromptDriver

            assert BasePromptDriver

    def test_deprecated_import_names_accessed_symbol_and_provider_package(self):
        with pytest.warns(DeprecationWarning, match="GriptapeCloudEventListenerDriver") as captured:
            from griptape.drivers import GriptapeCloudEventListenerDriver

        message = str(captured[0].message)
        assert message == (
            "Importing from `griptape.drivers` is deprecated and will be removed in a future release. "
            "Please import from the provider-specific package instead. "
            "Use `from griptape.drivers.event_listener.griptape_cloud import GriptapeCloudEventListenerDriver` "
            "instead."
        )
        # The private implementation module, not the documented package, must not be suggested.
        assert "griptape_cloud_event_listener_driver" not in message
        assert "OpenAiChatPromptDriver" not in message
        assert GriptapeCloudEventListenerDriver.__name__ == "GriptapeCloudEventListenerDriver"

    def test_deprecated_import_suggests_package_that_actually_exports_the_symbol(self):
        """Every deprecated name must be pointed at a real package that re-exports that exact object."""
        deprecated_module = importlib.import_module("griptape.drivers")
        names = sorted(set(deprecated_module.__all__))  # `__all__` repeats a handful of names

        values = {}
        suggestions = {}
        for name in names:
            with warnings.catch_warnings(record=True) as captured:
                warnings.simplefilter("always")
                values[name] = getattr(deprecated_module, name)
            assert len(captured) == 1, f"expected exactly one warning for {name}"
            match = re.search(r"Use `from (\S+) import (\S+)` instead\.", str(captured[0].message))
            assert match is not None, f"no replacement suggested for {name}"
            assert match.group(2) == name
            suggestions[name] = match.group(1)

        assert len(suggestions) == len(names)
        for name, package in suggestions.items():
            module = importlib.import_module(package)
            assert hasattr(module, "__path__"), f"{package} suggested for {name} is not a package"
            assert getattr(module, name) is values[name]

    def test_stream_usage_keeps_latest_running_total(self):
        # Providers like Anthropic (cumulative `message_delta` usage) and Gemini
        # (per-chunk `usage_metadata`) report running totals, not increments.
        driver = MockStreamUsagePromptDriver(
            stream=True,
            stream_usage_deltas=[
                DeltaMessage.Usage(input_tokens=100),
                DeltaMessage.Usage(output_tokens=1),
                DeltaMessage.Usage(output_tokens=2),
            ],
        )

        message = driver.run(PromptStack())

        assert message.usage.input_tokens == 100
        assert message.usage.output_tokens == 2

    def test_stream_usage_single_final_report(self):
        # Providers like OpenAI and Bedrock report a single final usage delta.
        driver = MockStreamUsagePromptDriver(
            stream=True,
            stream_usage_deltas=[DeltaMessage.Usage(input_tokens=7, output_tokens=9)],
        )

        message = driver.run(PromptStack())

        assert message.usage.input_tokens == 7
        assert message.usage.output_tokens == 9
