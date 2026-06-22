import base64
from collections.abc import Iterator
from copy import deepcopy
from unittest.mock import ANY, MagicMock, Mock

import httpx
import openai
import pytest
import schema

from griptape.artifacts import ActionArtifact, ImageArtifact, ListArtifact, TextArtifact
from griptape.artifacts.audio_artifact import AudioArtifact
from griptape.artifacts.generic_artifact import GenericArtifact
from griptape.artifacts.image_url_artifact import ImageUrlArtifact
from griptape.common import ActionCallDeltaMessageContent, PromptStack, TextDeltaMessageContent, ToolAction
from griptape.common.prompt_stack.contents.audio_delta_message_content import AudioDeltaMessageContent
from griptape.drivers.prompt.openai import OpenAiChatPromptDriver
from griptape.exceptions import PromptDriverError
from griptape.tokenizers import OpenAiTokenizer
from tests.mocks.mock_tokenizer import MockTokenizer
from tests.mocks.mock_tool.tool import MockTool


class TestOpenAiChatPromptDriverFixtureMixin:
    OPENAI_STRUCTURED_OUTPUT_SCHEMA = {
        "$id": "Output Format",
        "$schema": "http://json-schema.org/draft-07/schema#",
        "additionalProperties": False,
        "properties": {"foo": {"type": "string"}},
        "required": ["foo"],
        "type": "object",
    }
    OPENAI_TOOLS = [
        {
            "function": {
                "description": "test description: foo",
                "name": "MockTool_test",
                "parameters": {
                    "$id": "http://json-schema.org/draft-07/schema#",
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "additionalProperties": False,
                    "description": "Test input",
                    "properties": {"test": {"type": "string"}},
                    "required": ["test"],
                    "type": "object",
                },
            },
            "type": "function",
        },
        {
            "function": {
                "name": "MockTool_test_callable_schema",
                "description": "test description",
                "parameters": {
                    "description": "Test input",
                    "type": "object",
                    "properties": {"test": {"type": "string"}},
                    "required": ["test"],
                    "additionalProperties": False,
                    "$id": "http://json-schema.org/draft-07/schema#",
                    "$schema": "http://json-schema.org/draft-07/schema#",
                },
            },
            "type": "function",
        },
        {
            "function": {
                "description": "test description: foo",
                "name": "MockTool_test_error",
                "parameters": {
                    "$id": "http://json-schema.org/draft-07/schema#",
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "additionalProperties": False,
                    "description": "Test input",
                    "properties": {"test": {"type": "string"}},
                    "required": ["test"],
                    "type": "object",
                },
            },
            "type": "function",
        },
        {
            "function": {
                "description": "test description: foo",
                "name": "MockTool_test_exception",
                "parameters": {
                    "$id": "http://json-schema.org/draft-07/schema#",
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "additionalProperties": False,
                    "description": "Test input",
                    "properties": {"test": {"type": "string"}},
                    "required": ["test"],
                    "type": "object",
                },
            },
            "type": "function",
        },
        {
            "function": {
                "description": "test description",
                "name": "MockTool_test_list_output",
                "parameters": {
                    "$id": "http://json-schema.org/draft-07/schema#",
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "additionalProperties": False,
                    "properties": {},
                    "required": [],
                    "type": "object",
                },
            },
            "type": "function",
        },
        {
            "function": {
                "description": "test description",
                "name": "MockTool_test_no_schema",
                "parameters": {
                    "$id": "http://json-schema.org/draft-07/schema#",
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "additionalProperties": False,
                    "properties": {},
                    "required": [],
                    "type": "object",
                },
            },
            "type": "function",
        },
        {
            "function": {
                "description": "test description: foo",
                "name": "MockTool_test_str_output",
                "parameters": {
                    "$id": "http://json-schema.org/draft-07/schema#",
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "additionalProperties": False,
                    "description": "Test input",
                    "properties": {"test": {"type": "string"}},
                    "required": ["test"],
                    "type": "object",
                },
            },
            "type": "function",
        },
        {
            "function": {
                "description": "test description",
                "name": "MockTool_test_without_default_memory",
                "parameters": {
                    "$id": "http://json-schema.org/draft-07/schema#",
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "additionalProperties": False,
                    "description": "Test input",
                    "properties": {"test": {"type": "string"}},
                    "required": ["test"],
                    "type": "object",
                },
            },
            "type": "function",
        },
    ]

    @pytest.fixture()
    def mock_chat_completion_create(self, mocker):
        mock_chat_create = mocker.patch("openai.OpenAI").return_value.chat.completions.create
        mock_function = Mock(arguments='{"foo": "bar"}', id="mock-id")
        mock_function.name = "MockTool_test"
        mock_chat_create.return_value = Mock(
            headers={},
            choices=[
                Mock(
                    message=Mock(
                        content="model-output",
                        audio=Mock(
                            id="audio-id",
                            data=base64.b64encode(b"assistant-audio-data"),
                            transcript="assistant-audio-transcription",
                            expires_at=float("inf"),
                        ),
                        tool_calls=[Mock(id="mock-id", function=mock_function)],
                    )
                )
            ],
            usage=Mock(prompt_tokens=5, completion_tokens=10),
        )

        return mock_chat_create

    @pytest.fixture()
    def mock_chat_completion_stream_create(self, mocker):
        mock_chat_create = mocker.patch("openai.OpenAI").return_value.chat.completions.create
        mock_tool_call_delta_header = Mock()
        mock_tool_call_delta_header.name = "MockTool_test"
        mock_tool_call_delta_body = Mock(arguments='{"foo": "bar"}')
        mock_tool_call_delta_body.name = None

        mock_chat_create.return_value = iter(
            [
                Mock(choices=[Mock(delta=Mock(content="model-output", tool_calls=None))], usage=None),
                Mock(
                    choices=[
                        Mock(
                            delta=Mock(
                                content=None,
                                tool_calls=[Mock(index=0, id="mock-id", function=mock_tool_call_delta_header)],
                            )
                        )
                    ],
                    usage=None,
                ),
                Mock(
                    choices=[
                        Mock(
                            delta=Mock(
                                content=None, tool_calls=[Mock(index=0, id=None, function=mock_tool_call_delta_body)]
                            )
                        )
                    ],
                    usage=None,
                ),
                Mock(choices=None, usage=Mock(prompt_tokens=5, completion_tokens=10)),
                Mock(choices=[Mock(delta=Mock(content=None, tool_calls=None, audio=None))], usage=None),
                Mock(
                    choices=[
                        Mock(
                            delta=MagicMock(
                                content=None,
                                tool_calls=None,
                                audio={
                                    "id": "audio-id",
                                },
                            )
                        )
                    ],
                    usage=None,
                ),
                Mock(
                    choices=[
                        Mock(
                            delta=MagicMock(
                                content=None,
                                tool_calls=None,
                                audio={
                                    "data": base64.b64encode(b"assistant-audio-data").decode("utf-8"),
                                },
                            )
                        )
                    ],
                    usage=None,
                ),
                Mock(
                    choices=[
                        Mock(
                            delta=MagicMock(
                                content=None,
                                tool_calls=None,
                                audio={
                                    "expires_at": float("inf"),
                                    "transcript": "assistant-audio-transcription",
                                },
                            )
                        )
                    ],
                    usage=None,
                ),
            ]
        )
        return mock_chat_create

    @pytest.fixture()
    def prompt_stack(self):
        prompt_stack = PromptStack()
        prompt_stack.output_schema = schema.Schema({"foo": str})
        prompt_stack.tools = [MockTool()]
        prompt_stack.add_system_message("system-input")
        prompt_stack.add_user_message("user-input")
        prompt_stack.add_user_message(
            ListArtifact(
                [
                    TextArtifact("user-input"),
                    ImageArtifact(value=b"image-data", format="png", width=100, height=100),
                    ImageUrlArtifact(value="image-url"),
                ]
            )
        )
        prompt_stack.add_assistant_message("assistant-input")
        prompt_stack.add_assistant_message(
            ListArtifact(
                [
                    ActionArtifact(ToolAction(tag="MockTool_test", name="MockTool", path="test", input={"foo": "bar"})),
                ]
            )
        )
        prompt_stack.add_user_message(
            ListArtifact(
                [
                    TextArtifact("keep-going"),
                    ActionArtifact(
                        ToolAction(
                            tag="MockTool_test",
                            name="MockTool",
                            path="test",
                            input={"foo": "bar"},
                            output=TextArtifact("tool-output"),
                        )
                    ),
                ]
            )
        )
        prompt_stack.add_user_message(
            AudioArtifact(
                value=b"user-audio-data",
                format="wav",
            ),
        )
        prompt_stack.add_assistant_message(
            AudioArtifact(
                value=b"assistant-audio-data",
                format="wav",
                meta={
                    "audio_id": "audio-id",
                    "transcript": "assistant-audio-transcription",
                    "expires_at": float("inf"),
                },
            ),
        )
        prompt_stack.add_assistant_message(
            AudioArtifact(
                value=b"assistant-audio-data",
                format="wav",
                meta={
                    "audio_id": "audio-id",
                    "transcript": "assistant-audio-transcription",
                    "expires_at": float("-inf"),
                },
            ),
        )

        prompt_stack.add_user_message(GenericArtifact(value="generic-value"))
        return prompt_stack

    @pytest.fixture()
    def messages(self):
        return [
            {"role": "system", "content": "system-input"},
            {"role": "user", "content": "user-input"},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "user-input"},
                    {"type": "image_url", "image_url": {"url": "data:image/png;base64,aW1hZ2UtZGF0YQ=="}},
                    {"type": "image_url", "image_url": {"url": "image-url"}},
                ],
            },
            {"role": "assistant", "content": "assistant-input"},
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "function": {"arguments": '{"foo": "bar"}', "name": "MockTool_test"},
                        "id": "MockTool_test",
                        "type": "function",
                    }
                ],
            },
            {"content": "tool-output", "role": "tool", "tool_call_id": "MockTool_test"},
            {"content": "keep-going", "role": "user"},
            {
                "content": [
                    {"type": "input_audio", "input_audio": {"data": "dXNlci1hdWRpby1kYXRh", "format": "wav"}},
                ],
                "role": "user",
            },
            {"audio": {"id": "audio-id"}, "role": "assistant"},
            {"content": [{"type": "text", "text": "assistant-audio-transcription"}], "role": "assistant"},
            {"content": [{"type": "text", "text": "generic-value"}], "role": "user"},
        ]

    @pytest.fixture()
    def reasoning_messages(self, messages):
        messages = deepcopy(messages)
        for message in messages:
            if message["role"] == "system":
                message["role"] = "developer"
        return messages


class OpenAiApiResponseWithHeaders:
    def __init__(
        self,
        reset_requests_in=5,
        reset_requests_in_unit="s",
        reset_tokens_in=10,
        reset_tokens_in_unit="s",
        remaining_requests=123,
        remaining_tokens=234,
        limit_requests=345,
        limit_tokens=456,
    ) -> None:
        self.reset_requests_in = reset_requests_in
        self.reset_requests_in_unit = reset_requests_in_unit
        self.reset_tokens_in = reset_tokens_in
        self.reset_tokens_in_unit = reset_tokens_in_unit
        self.remaining_requests = remaining_requests
        self.remaining_tokens = remaining_tokens
        self.limit_requests = limit_requests
        self.limit_tokens = limit_tokens

    @property
    def headers(self):
        return {
            "x-ratelimit-reset-requests": f"{self.reset_requests_in}{self.reset_requests_in_unit}",
            "x-ratelimit-reset-tokens": f"{self.reset_tokens_in}{self.reset_tokens_in_unit}",
            "x-ratelimit-limit-requests": self.limit_requests,
            "x-ratelimit-remaining-requests": self.remaining_requests,
            "x-ratelimit-limit-tokens": self.limit_tokens,
            "x-ratelimit-remaining-tokens": self.remaining_tokens,
        }


class TestOpenAiChatPromptDriver(TestOpenAiChatPromptDriverFixtureMixin):
    def test_init(self):
        assert OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_4_MODEL)

    @pytest.mark.parametrize(
        ("model", "expected"),
        [
            ("gpt-4", True),
            ("gpt-4.1", True),
            ("gpt-4o", True),
            ("gpt-3.5-turbo", True),
            ("gpt-5", False),
            ("gpt-5-turbo", False),
            ("o1", False),
            ("o1-preview", False),
            ("o1-mini", False),
            ("o3", False),
            ("o3-mini", False),
        ],
    )
    def test_supports_stop_sequences(self, model, expected):
        driver = OpenAiChatPromptDriver(model=model)
        assert driver.supports_stop_sequences == expected

    @pytest.mark.parametrize(
        ("model", "expected"),
        [
            ("gpt-4", True),
            ("gpt-4.1", True),
            ("gpt-4o", True),
            ("gpt-3.5-turbo", True),
            ("gpt-5", True),
            ("gpt-5-turbo", True),
            ("o1", False),
            ("o1-preview", False),
            ("o1-mini", False),
            ("o3", False),
            ("o3-mini", False),
        ],
    )
    def test_supports_modalities(self, model, expected):
        driver = OpenAiChatPromptDriver(model=model)
        assert driver.supports_modalities == expected

    @pytest.mark.parametrize(
        ("model", "expected"),
        [
            ("gpt-4", False),
            ("gpt-4.1", False),
            ("gpt-4o", False),
            ("gpt-3.5-turbo", False),
            ("gpt-5", False),
            ("gpt-5-turbo", False),
            ("o1", True),
            ("o1-preview", True),
            ("o1-mini", False),  # Special case: o1-mini doesn't support reasoning_effort
            ("o3", True),
            ("o3-mini", True),
        ],
    )
    def test_supports_reasoning_effort(self, model, expected):
        driver = OpenAiChatPromptDriver(model=model)
        assert driver.supports_reasoning_effort == expected

    @pytest.mark.parametrize(
        ("model", "expected"),
        [
            ("gpt-4", True),
            ("gpt-4.1", True),
            ("gpt-4o", True),
            ("gpt-3.5-turbo", True),
            ("gpt-5", False),  # GPT-5 doesn't support custom temperature
            ("gpt-5-turbo", False),  # GPT-5 doesn't support custom temperature
            ("o1", False),  # O-series models don't support custom temperature
            ("o1-preview", False),
            ("o1-mini", False),
            ("o3", False),
            ("o3-mini", False),
        ],
    )
    def test_supports_temperature(self, model, expected):
        driver = OpenAiChatPromptDriver(model=model)
        assert driver.supports_temperature == expected

    @pytest.mark.parametrize(
        ("model", "expected_role", "expected_temp", "expected_reasoning"),
        [
            # GPT models (non-reasoning): support stop sequences, temperature, no reasoning effort
            ("gpt-4.1", "system", True, False),
            ("gpt-4o", "system", True, False),
            # GPT-5 models: no stop sequences (developer role), NO temperature, no reasoning effort
            ("gpt-5", "developer", False, False),
            ("gpt-5-turbo", "developer", False, False),
            # O1 models: no stop sequences (developer role), NO temperature, reasoning effort (except mini)
            ("o1", "developer", False, True),
            ("o1-preview", "developer", False, True),
            ("o1-mini", "developer", False, False),  # Special case: no reasoning effort and no temperature
            ("o3", "developer", False, True),
            ("o3-mini", "developer", False, True),
        ],
    )
    def test_model_behavioral_differences(self, model, expected_role, expected_temp, expected_reasoning):
        driver = OpenAiChatPromptDriver(model=model)

        # Test role mapping
        from griptape.common import Message

        system_message = Message(content=[], role=Message.SYSTEM_ROLE)
        actual_role = driver._OpenAiChatPromptDriver__to_openai_role(system_message)
        assert actual_role == expected_role

        # Test temperature inclusion
        params = driver._base_params(PromptStack())
        has_temperature = "temperature" in params
        assert has_temperature == expected_temp

        # Test reasoning effort inclusion
        has_reasoning_effort = "reasoning_effort" in params
        assert has_reasoning_effort == expected_reasoning

    @pytest.mark.parametrize("use_native_tools", [True, False])
    @pytest.mark.parametrize("structured_output_strategy", ["native", "tool", "rule", "foo"])
    @pytest.mark.parametrize("model", ["gpt-4.1", "gpt-5", "o1", "o1-mini", "o3", "o3-mini"])
    @pytest.mark.parametrize("modalities", [[], ["text"], ["text", "audio"], ["audio"]])
    def test_try_run(
        self,
        mock_chat_completion_create,
        prompt_stack,
        reasoning_messages,
        messages,
        use_native_tools,
        structured_output_strategy,
        model,
        modalities,
    ):
        # Given
        driver = OpenAiChatPromptDriver(
            model=model,
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
            **{
                "user": driver.user,
            }
            if driver.user
            else {},
            messages=reasoning_messages if not driver.supports_stop_sequences else messages,
            **{
                "seed": driver.seed,
            }
            if driver.seed is not None
            else {},
            **{
                "modalities": driver.modalities,
            }
            if driver.modalities and driver.supports_modalities
            else {},
            **{
                "audio": driver.audio,
            }
            if "audio" in driver.modalities
            else {},
            **{
                "reasoning_effort": driver.reasoning_effort,
            }
            if driver.supports_reasoning_effort
            else {},
            **{
                "temperature": driver.temperature,
            }
            if driver.supports_stop_sequences
            else {},
            **{
                "tools": self.OPENAI_TOOLS,
                "tool_choice": "required" if structured_output_strategy == "tool" else driver.tool_choice,
                "parallel_tool_calls": driver.parallel_tool_calls,
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
            if prompt_stack.output_schema is not None and structured_output_strategy == "native"
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

    def test_try_run_response_format_json_object(self, mock_chat_completion_create, prompt_stack, messages):
        # Given
        driver = OpenAiChatPromptDriver(
            model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL,
            response_format={"type": "json_object"},
            use_native_tools=False,
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
            messages=[*messages, {"role": "system", "content": "Provide your response as a valid JSON object."}],
            **{
                "seed": driver.seed,
            }
            if driver.seed is not None
            else {},
            **{
                "audio": driver.audio,
            }
            if "audio" in driver.modalities
            else {},
            **{
                "modalities": driver.modalities,
            }
            if driver.modalities and driver.supports_modalities
            else {},
            response_format={"type": "json_object"},
        )
        assert message.value[0].value == "model-output"
        assert message.usage.input_tokens == 5
        assert message.usage.output_tokens == 10

    def test_try_run_response_format_json_schema(self, mock_chat_completion_create, prompt_stack, messages):
        # Given
        driver = OpenAiChatPromptDriver(
            model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "strict": True,
                    "name": "OutputSchema",
                    "schema": schema.Schema({"test": str}).json_schema("Output Schema"),
                },
            },
            use_native_tools=False,
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
            messages=[*messages],
            **{
                "seed": driver.seed,
            }
            if driver.seed is not None
            else {},
            **{
                "audio": driver.audio,
            }
            if "audio" in driver.modalities
            else {},
            **{
                "modalities": driver.modalities,
            }
            if driver.modalities and driver.supports_modalities
            else {},
            response_format={
                "json_schema": {
                    "schema": {
                        "$id": "Output Schema",
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "additionalProperties": False,
                        "properties": {"test": {"type": "string"}},
                        "required": ["test"],
                        "type": "object",
                    },
                    "name": "OutputSchema",
                    "strict": True,
                },
                "type": "json_schema",
            },
        )
        assert message.value[0].value == "model-output"
        assert message.usage.input_tokens == 5
        assert message.usage.output_tokens == 10

    @pytest.mark.parametrize("use_native_tools", [True, False])
    @pytest.mark.parametrize("structured_output_strategy", ["native", "tool", "rule", "foo"])
    @pytest.mark.parametrize("model", ["gpt-4.1", "gpt-5", "o1", "o1-mini", "o3", "o3-mini"])
    @pytest.mark.parametrize("modalities", [[], ["text"], ["text", "audio"], ["audio"]])
    def test_try_stream_run(
        self,
        mock_chat_completion_stream_create,
        prompt_stack,
        reasoning_messages,
        messages,
        use_native_tools,
        structured_output_strategy,
        model,
        modalities,
    ):
        # Given
        driver = OpenAiChatPromptDriver(
            model=model,
            stream=True,
            use_native_tools=use_native_tools,
            structured_output_strategy=structured_output_strategy,
            extra_params={"foo": "bar"},
            modalities=modalities,
        )

        # When
        stream = driver.try_stream(prompt_stack)
        event = next(stream)

        # Then
        mock_chat_completion_stream_create.assert_called_once_with(
            model=driver.model,
            **{
                "user": driver.user,
            }
            if driver.user
            else {},
            stream=True,
            messages=reasoning_messages if not driver.supports_stop_sequences else messages,
            **{
                "seed": driver.seed,
            }
            if driver.seed is not None
            else {},
            stream_options={"include_usage": True},
            **{
                "audio": driver.audio,
            }
            if "audio" in driver.modalities
            else {},
            **{"modalities": driver.modalities} if driver.modalities and driver.supports_modalities else {},
            **{"reasoning_effort": driver.reasoning_effort} if driver.supports_reasoning_effort else {},
            **{
                "temperature": driver.temperature,
            }
            if driver.supports_stop_sequences
            else {},
            **{
                "tools": self.OPENAI_TOOLS,
                "tool_choice": "required" if structured_output_strategy == "tool" else driver.tool_choice,
                "parallel_tool_calls": driver.parallel_tool_calls,
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

    def test_try_run_with_max_tokens(self, mock_chat_completion_create, prompt_stack, messages):
        # Given
        prompt_stack.output_schema = None
        driver = OpenAiChatPromptDriver(
            model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL,
            max_tokens=1,
            use_native_tools=False,
        )

        # When
        event = driver.try_run(prompt_stack)

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
            max_tokens=1,
            **{
                "seed": driver.seed,
            }
            if driver.seed is not None
            else {},
            **{
                "audio": driver.audio,
            }
            if "audio" in driver.modalities
            else {},
            **{
                "modalities": driver.modalities,
            }
            if driver.modalities and driver.supports_modalities
            else {},
        )
        assert event.value[0].value == "model-output"

    def test_try_run_throws_when_multiple_choices_returned(self, mock_chat_completion_create, prompt_stack):
        # Given
        driver = OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL, api_key="api-key")
        mock_chat_completion_create.return_value.choices = [Mock(message=Mock(content="model-output"))] * 10

        # When
        with pytest.raises(Exception) as e:
            driver.try_run(prompt_stack)

        # Then
        assert e.value.args[0] == "Completion with more than one choice is not supported yet."

    def test_custom_tokenizer(self, mock_chat_completion_create, prompt_stack, messages):
        prompt_stack.output_schema = None
        driver = OpenAiChatPromptDriver(
            model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL,
            tokenizer=MockTokenizer(model="mock-model", stop_sequences=["mock-stop"]),
            max_tokens=1,
            use_native_tools=False,
        )

        # When
        event = driver.try_run(prompt_stack)

        # Then
        mock_chat_completion_create.assert_called_once_with(
            model=driver.model,
            temperature=driver.temperature,
            stop=driver.tokenizer.stop_sequences,
            **{
                "user": driver.user,
            }
            if driver.user
            else {},
            messages=messages,
            **{
                "seed": driver.seed,
            }
            if driver.seed is not None
            else {},
            **{
                "audio": driver.audio,
            }
            if "audio" in driver.modalities
            else {},
            **{
                "modalities": driver.modalities,
            }
            if driver.modalities and driver.supports_modalities
            else {},
            max_tokens=1,
        )
        assert event.value[0].value == "model-output"


class TestOpenAiChatPromptDriverExceptionWrapping(TestOpenAiChatPromptDriverFixtureMixin):
    """#1946 — OpenAI SDK exceptions are wrapped as Griptape ``PromptDriverError``."""

    @pytest.fixture()
    def simple_prompt_stack(self):
        prompt_stack = PromptStack()
        prompt_stack.add_user_message("hello")
        return prompt_stack

    @staticmethod
    def _openai_status_error(error_cls: type[openai.APIStatusError], status_code: int) -> openai.APIStatusError:
        request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
        response = httpx.Response(status_code, request=request)
        return error_cls("boom", response=response, body=None)

    def _driver(self, **kwargs):
        return OpenAiChatPromptDriver(
            model="gpt-4o", api_key="x", tokenizer=MockTokenizer(model="test-model"), **kwargs
        )

    def test_run_wraps_openai_status_error(self, mock_chat_completion_create, simple_prompt_stack):
        mock_chat_completion_create.side_effect = self._openai_status_error(openai.AuthenticationError, 401)

        with pytest.raises(PromptDriverError) as exc_info:
            self._driver().run(simple_prompt_stack)

        assert exc_info.value.status_code == 401
        assert isinstance(exc_info.value.__cause__, openai.AuthenticationError)

    def test_run_does_not_retry_4xx(self, mock_chat_completion_create, simple_prompt_stack):
        mock_chat_completion_create.side_effect = self._openai_status_error(openai.BadRequestError, 400)

        with pytest.raises(PromptDriverError):
            self._driver(max_attempts=2, min_retry_delay=0, max_retry_delay=0).run(simple_prompt_stack)

        assert mock_chat_completion_create.call_count == 1  # fast-fail: not retried

    def test_run_retries_then_wraps_429(self, mock_chat_completion_create, simple_prompt_stack):
        mock_chat_completion_create.side_effect = self._openai_status_error(openai.RateLimitError, 429)

        with pytest.raises(PromptDriverError) as exc_info:
            self._driver(max_attempts=2, min_retry_delay=0, max_retry_delay=0).run(simple_prompt_stack)

        assert exc_info.value.status_code == 429
        assert mock_chat_completion_create.call_count == 2  # retried up to max_attempts

    def test_run_does_not_wrap_non_openai_exception(self, mock_chat_completion_create, simple_prompt_stack):
        mock_chat_completion_create.side_effect = ValueError("internal griptape error")

        with pytest.raises(ValueError):
            self._driver(max_attempts=1, min_retry_delay=0, max_retry_delay=0).run(simple_prompt_stack)

    def test_stream_wraps_openai_status_error(self, mock_chat_completion_create, simple_prompt_stack):
        mock_chat_completion_create.side_effect = self._openai_status_error(openai.AuthenticationError, 401)

        with pytest.raises(PromptDriverError) as exc_info:
            self._driver(stream=True).run(simple_prompt_stack)

        assert exc_info.value.status_code == 401
        assert isinstance(exc_info.value.__cause__, openai.AuthenticationError)

    def test_run_wraps_connection_error_with_status_none(self, mock_chat_completion_create, simple_prompt_stack):
        request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
        mock_chat_completion_create.side_effect = openai.APIConnectionError(request=request)

        with pytest.raises(PromptDriverError) as exc_info:
            self._driver(max_attempts=1, min_retry_delay=0, max_retry_delay=0).run(simple_prompt_stack)

        assert exc_info.value.status_code is None
        assert isinstance(exc_info.value.__cause__, openai.APIConnectionError)

    def test_stream_wraps_error_raised_mid_iteration(self, mock_chat_completion_create, simple_prompt_stack):
        error = self._openai_status_error(openai.InternalServerError, 500)

        def exploding_stream() -> Iterator[object]:
            yield from ()
            raise error

        mock_chat_completion_create.return_value = exploding_stream()

        with pytest.raises(PromptDriverError) as exc_info:
            self._driver(stream=True, max_attempts=1, min_retry_delay=0, max_retry_delay=0).run(simple_prompt_stack)

        assert exc_info.value.status_code == 500
        assert isinstance(exc_info.value.__cause__, openai.InternalServerError)
