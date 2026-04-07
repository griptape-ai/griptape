from unittest.mock import ANY

import pytest

from griptape.artifacts import ActionArtifact, AudioArtifact, TextArtifact
from griptape.common import ActionCallDeltaMessageContent, AudioDeltaMessageContent, TextDeltaMessageContent
from griptape.drivers.prompt.grok import GrokPromptDriver
from tests.unit.drivers.prompt.test_openai_chat_prompt_driver import TestOpenAiChatPromptDriverFixtureMixin


class TestGrokPromptDriver(TestOpenAiChatPromptDriverFixtureMixin):
    def test_init(self):
        assert GrokPromptDriver(api_key="foo", model="gpt-4")

    @pytest.mark.parametrize("use_native_tools", [True, False])
    @pytest.mark.parametrize("structured_output_strategy", ["native", "tool"])
    @pytest.mark.parametrize("modalities", [["text"], ["text", "audio"], ["audio"]])
    def test_try_run(
        self,
        mock_chat_completion_create,
        prompt_stack,
        messages,
        use_native_tools,
        structured_output_strategy,
        modalities,
    ):
        # Given
        driver = GrokPromptDriver(
            model="grok-2-latest",
            use_native_tools=use_native_tools,
            structured_output_strategy=structured_output_strategy,
            modalities=modalities,
            extra_params={"foo": "bar"},
        )

        # When
        message = driver.try_run(prompt_stack)

        # Then
        mock_chat_completion_create.assert_called_once_with(
            model=driver.model,
            temperature=driver.temperature,
            **{
                "user": driver.user,
            }
            if driver.user
            else {},
            messages=messages,
            modalities=modalities,
            **{
                "audio": driver.audio,
            }
            if "audio" in driver.modalities
            else {},
            **{
                "seed": driver.seed,
            }
            if driver.seed is not None
            else {},
            **{
                "parallel_tool_calls": driver.parallel_tool_calls,
            }
            if prompt_stack.tools and driver.use_native_tools
            else {},
            **{
                "tools": self.OPENAI_TOOLS,
                "tool_choice": "required" if structured_output_strategy == "tool" else driver.tool_choice,
            }
            if use_native_tools
            else {},
            **{
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "Output",
                        "schema": self.OPENAI_STRUCTURED_OUTPUT_SCHEMA,
                        "strict": True,
                    },
                }
            }
            if structured_output_strategy == "native"
            else {},
            foo="bar",
        )
        assert isinstance(message.value[0], TextArtifact)
        assert message.value[0].value == "model-output"
        assert isinstance(message.value[1], AudioArtifact)
        assert message.value[1].value == b"assistant-audio-data"
        assert message.value[1].format == "wav"
        assert message.value[1].meta == {
            "audio_id": "audio-id",
            "transcript": "assistant-audio-transcription",
            "expires_at": ANY,
        }
        assert isinstance(message.value[2], ActionArtifact)
        assert message.value[2].value.tag == "mock-id"
        assert message.value[2].value.name == "MockTool"
        assert message.value[2].value.path == "test"
        assert message.value[2].value.input == {"foo": "bar"}

    @pytest.mark.parametrize("use_native_tools", [True, False])
    @pytest.mark.parametrize("structured_output_strategy", ["native", "tool"])
    @pytest.mark.parametrize("modalities", [["text"], ["text", "audio"], ["audio"]])
    def test_try_stream_run(
        self,
        mock_chat_completion_stream_create,
        prompt_stack,
        messages,
        use_native_tools,
        structured_output_strategy,
        modalities,
    ):
        # Given
        driver = GrokPromptDriver(
            model="grok-2-latest",
            stream=True,
            modalities=modalities,
            use_native_tools=use_native_tools,
            structured_output_strategy=structured_output_strategy,
            extra_params={"foo": "bar"},
        )

        # When
        stream = driver.try_stream(prompt_stack)
        event = next(stream)

        # Then
        mock_chat_completion_stream_create.assert_called_once_with(
            model=driver.model,
            temperature=driver.temperature,
            **{
                "user": driver.user,
            }
            if driver.user
            else {},
            **{
                "audio": driver.audio,
            }
            if "audio" in driver.modalities
            else {},
            stream=True,
            messages=messages,
            modalities=modalities,
            **{
                "tools": self.OPENAI_TOOLS,
                "tool_choice": "required" if structured_output_strategy == "tool" else driver.tool_choice,
            }
            if use_native_tools
            else {},
            **{
                "seed": driver.seed,
            }
            if driver.seed is not None
            else {},
            **{
                "parallel_tool_calls": driver.parallel_tool_calls,
            }
            if prompt_stack.tools and driver.use_native_tools
            else {},
            **{
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "Output",
                        "schema": self.OPENAI_STRUCTURED_OUTPUT_SCHEMA,
                        "strict": True,
                    },
                }
            }
            if structured_output_strategy == "native"
            else {},
            foo="bar",
            stream_options={"include_usage": True},
        )

        assert isinstance(event.content, TextDeltaMessageContent)
        assert event.content.text == "model-output"

        event = next(stream)
        assert isinstance(event.content, ActionCallDeltaMessageContent)
        assert event.content.tag == "mock-id"
        assert event.content.name == "MockTool"
        assert event.content.path == "test"

        event = next(stream)
        assert isinstance(event.content, ActionCallDeltaMessageContent)
        assert event.content.partial_input == '{"foo": "bar"}'

        event = next(stream)
        assert event.usage.input_tokens == 5
        assert event.usage.output_tokens == 10

        event = next(stream)
        assert isinstance(event.content, AudioDeltaMessageContent)
        assert event.content.id == "audio-id"

        event = next(stream)
        assert isinstance(event.content, AudioDeltaMessageContent)
        assert event.content.data == "YXNzaXN0YW50LWF1ZGlvLWRhdGE="

        event = next(stream)
        assert isinstance(event.content, AudioDeltaMessageContent)
        assert event.content.expires_at == ANY
        assert event.content.transcript == "assistant-audio-transcription"

    def test_to_dict(self):
        # Given
        driver = GrokPromptDriver(
            model="grok-2-latest",
            use_native_tools=True,
            structured_output_strategy="native",
            modalities=["text", "audio"],
            extra_params={"foo": "bar"},
        )

        # When
        result = driver.to_dict()

        # Then
        assert result == {
            "audio": {"format": "pcm16", "voice": "alloy"},
            "base_url": "https://api.x.ai/v1",
            "extra_params": {"foo": "bar"},
            "max_tokens": None,
            "modalities": ["text", "audio"],
            "model": "grok-2-latest",
            "organization": None,
            "parallel_tool_calls": True,
            "reasoning_effort": "medium",
            "response_format": None,
            "seed": None,
            "stream": False,
            "structured_output_strategy": "native",
            "temperature": 0.1,
            "tokenizer": {
                "base_url": "https://api.x.ai/v1",
                "max_input_tokens": 131072,
                "max_output_tokens": 4096,
                "model": "grok-2-latest",
                "stop_sequences": [],
                "type": "GrokTokenizer",
            },
            "type": "GrokPromptDriver",
            "use_native_tools": True,
            "user": "",
        }

    def test_from_dict(self):
        # Given
        driver = GrokPromptDriver(
            model="grok-2-latest",
            use_native_tools=True,
            structured_output_strategy="native",
            modalities=["text", "audio"],
            extra_params={"foo": "bar"},
        )

        # When
        result = GrokPromptDriver.from_dict(driver.to_dict())

        # Then
        assert result.to_dict() == driver.to_dict()
