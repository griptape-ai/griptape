import json
import time
from unittest.mock import ANY, MagicMock

import pytest
from schema import Schema

from griptape.artifacts import ActionArtifact, AudioArtifact, ImageArtifact, ListArtifact, TextArtifact
from griptape.common import ActionCallDeltaMessageContent, PromptStack, TextDeltaMessageContent, ToolAction
from griptape.common.prompt_stack.contents.audio_delta_message_content import AudioDeltaMessageContent
from griptape.drivers.prompt.griptape_cloud import GriptapeCloudPromptDriver
from tests.mocks.mock_tool.tool import MockTool


class TestGriptapeCloudPromptDriver:
    GRIPTAPE_CLOUD_STRUCTURED_OUTPUT_SCHEMA = {
        "$id": "Output Format",
        "$schema": "http://json-schema.org/draft-07/schema#",
        "additionalProperties": False,
        "properties": {"foo": {"type": "string"}},
        "required": ["foo"],
        "type": "object",
    }
    GRIPTAPE_CLOUD_TOOLS = [
        {
            "activities": [
                {
                    "description": "test description: foo",
                    "json_schema": {
                        "$id": "Schema",
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "additionalProperties": False,
                        "properties": {
                            "values": {
                                "additionalProperties": False,
                                "description": "Test input",
                                "properties": {
                                    "test": {"type": "string"},
                                },
                                "required": ["test"],
                                "type": "object",
                            },
                        },
                        "required": ["values"],
                        "type": "object",
                    },
                    "name": "test",
                },
                {
                    "description": "test description",
                    "json_schema": {
                        "$id": "Schema",
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "additionalProperties": False,
                        "properties": {
                            "values": {
                                "additionalProperties": False,
                                "description": "Test input",
                                "properties": {
                                    "test": {"type": "string"},
                                },
                                "required": ["test"],
                                "type": "object",
                            },
                        },
                        "required": ["values"],
                        "type": "object",
                    },
                    "name": "test_callable_schema",
                },
                {
                    "description": "test description: foo",
                    "json_schema": {
                        "$id": "Schema",
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "additionalProperties": False,
                        "properties": {
                            "values": {
                                "additionalProperties": False,
                                "description": "Test input",
                                "properties": {
                                    "test": {"type": "string"},
                                },
                                "required": ["test"],
                                "type": "object",
                            },
                        },
                        "required": ["values"],
                        "type": "object",
                    },
                    "name": "test_error",
                },
                {
                    "description": "test description: foo",
                    "json_schema": {
                        "$id": "Schema",
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "additionalProperties": False,
                        "properties": {
                            "values": {
                                "additionalProperties": False,
                                "description": "Test input",
                                "properties": {
                                    "test": {"type": "string"},
                                },
                                "required": ["test"],
                                "type": "object",
                            },
                        },
                        "required": ["values"],
                        "type": "object",
                    },
                    "name": "test_exception",
                },
                {
                    "description": "test description",
                    "json_schema": {
                        "$id": "Schema",
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "additionalProperties": False,
                        "properties": {},
                        "required": [],
                        "type": "object",
                    },
                    "name": "test_list_output",
                },
                {
                    "description": "test description",
                    "json_schema": {
                        "$id": "Schema",
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "additionalProperties": False,
                        "properties": {},
                        "required": [],
                        "type": "object",
                    },
                    "name": "test_no_schema",
                },
                {
                    "description": "test description: foo",
                    "json_schema": {
                        "$id": "Schema",
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "additionalProperties": False,
                        "properties": {
                            "values": {
                                "additionalProperties": False,
                                "description": "Test input",
                                "properties": {
                                    "test": {"type": "string"},
                                },
                                "required": ["test"],
                                "type": "object",
                            },
                        },
                        "required": ["values"],
                        "type": "object",
                    },
                    "name": "test_str_output",
                },
                {
                    "description": "test description",
                    "json_schema": {
                        "$id": "Schema",
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "additionalProperties": False,
                        "properties": {
                            "values": {
                                "additionalProperties": False,
                                "description": "Test input",
                                "properties": {
                                    "test": {"type": "string"},
                                },
                                "required": ["test"],
                                "type": "object",
                            },
                        },
                        "required": ["values"],
                        "type": "object",
                    },
                    "name": "test_without_default_memory",
                },
            ],
            "name": "MockTool",
        },
    ]

    @pytest.fixture(autouse=True)
    def mock_post(self, mocker):
        def request(*args, **kwargs):
            mock_response = mocker.Mock()
            if "chat/messages/stream" in args[0]:
                mock_response.iter_lines.return_value = [
                    f"data: {json.dumps(event)}".encode()
                    for event in [
                        {
                            "type": "DeltaMessage",
                            "content": {"type": "TextDeltaMessageContent", "text": "model-output"},
                            "role": "assistant",
                        },
                        {
                            "type": "DeltaMessage",
                            "content": {
                                "type": "ActionCallDeltaMessageContent",
                                "tag": "MockTool_test",
                                "name": "MockTool",
                                "path": "test",
                                "partial_input": json.dumps({"foo": "bar"}),
                                "index": 0,
                            },
                            "role": "assistant",
                        },
                        {
                            "type": "DeltaMessage",
                            "content": {
                                "type": "ActionCallDeltaMessageContent",
                                "tag": "MockTool_test",
                                "name": "MockTool",
                                "path": "test",
                                "partial_input": json.dumps({"foo": "bar"}),
                                "index": 1,
                            },
                            "role": "assistant",
                        },
                        {
                            "type": "DeltaMessage",
                            "content": {"type": "AudioDeltaMessageContent", "data": "YXNzaXN0YW50LWF1ZGlvLWRhdGE="},
                            "role": "assistant",
                        },
                        {
                            "type": "DeltaMessage",
                            "content": {
                                "type": "AudioDeltaMessageContent",
                                "expires_at": time.time() + 1000,
                                "transcript": "assistant-audio-transcription",
                            },
                            "role": "assistant",
                        },
                    ]
                ]

                mock_response.__enter__ = MagicMock(return_value=mock_response)
                mock_response.__exit__ = MagicMock()
                return mock_response
            if "chat/messages" in args[0]:
                mock_response.json.return_value = {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "TextMessageContent",
                            "artifact": {"type": "TextArtifact", "value": "text-model-output"},
                        },
                        {
                            "type": "ActionCallMessageContent",
                            "artifact": {
                                "type": "ActionArtifact",
                                "value": {
                                    "type": "ToolAction",
                                    "tag": "MockTool_test",
                                    "name": "MockTool",
                                    "path": "test",
                                    "input": {"foo": "bar"},
                                },
                            },
                        },
                        {
                            "type": "AudioMessageContent",
                            "artifact": {
                                "type": "AudioArtifact",
                                "value": b"YXVkaW8tbW9kZWwtb3V0cHV0",
                                "format": "wav",
                            },
                        },
                    ],
                }
                return mock_response
            return mocker.Mock(
                raise_for_status=lambda: None,
            )

        return mocker.patch("requests.post", side_effect=request)

    @pytest.fixture()
    def prompt_stack(self):
        prompt_stack = PromptStack()
        prompt_stack.output_schema = Schema({"foo": str})
        prompt_stack.tools = [MockTool()]
        prompt_stack.add_system_message("system-input")
        prompt_stack.add_user_message("user-input")
        prompt_stack.add_user_message(
            ListArtifact(
                [TextArtifact("user-input"), ImageArtifact(value=b"image-data", format="png", width=100, height=100)]
            )
        )
        prompt_stack.add_assistant_message("assistant-input")
        prompt_stack.add_assistant_message(
            ListArtifact(
                [
                    TextArtifact(""),
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
        return prompt_stack

    def test_init(self):
        assert GriptapeCloudPromptDriver(api_key="foo", model="gpt-4.1")

    @pytest.mark.parametrize("model", [None, "gpt-4.1"])
    @pytest.mark.parametrize("use_native_tools", [True, False])
    @pytest.mark.parametrize("structured_output_strategy", ["native", "tool", "rule", "foo"])
    def test_try_run(
        self,
        mock_post,
        prompt_stack,
        model,
        use_native_tools,
        structured_output_strategy,
    ):
        # Given
        driver = GriptapeCloudPromptDriver(
            api_key="foo",
            model=model,
            use_native_tools=use_native_tools,
            structured_output_strategy=structured_output_strategy,
            extra_params={"foo": "bar"},
        )

        # When
        message = driver.try_run(prompt_stack)

        # Then
        mock_post.assert_called_once_with(
            "https://cloud.griptape.ai/api/chat/messages",
            headers={"Authorization": f"Bearer {driver.api_key}"},
            json={
                "messages": prompt_stack.to_dict()["messages"],
                "tools": self.GRIPTAPE_CLOUD_TOOLS,
                "output_schema": self.GRIPTAPE_CLOUD_STRUCTURED_OUTPUT_SCHEMA,
                "driver_configuration": {
                    **({"model": model} if model else {}),
                    "max_tokens": driver.max_tokens,
                    "use_native_tools": use_native_tools,
                    "temperature": driver.temperature,
                    "structured_output_strategy": structured_output_strategy,
                    "extra_params": {"foo": "bar"},
                },
            },
        )
        assert isinstance(message.value[0], TextArtifact)
        assert message.value[0].value == "text-model-output"
        assert isinstance(message.value[1], ActionArtifact)
        assert message.value[1].value.tag == "MockTool_test"
        assert message.value[1].value.name == "MockTool"
        assert message.value[1].value.path == "test"
        assert message.value[1].value.input == {"foo": "bar"}

        assert isinstance(message.value[2], AudioArtifact)
        assert message.value[2].value == b"audio-model-output"
        assert message.value[2].format == "wav"

    @pytest.mark.parametrize("model", [None, "gpt-4.1"])
    @pytest.mark.parametrize("use_native_tools", [True, False])
    @pytest.mark.parametrize("structured_output_strategy", ["native", "tool", "rule", "foo"])
    def test_try_stream_run(
        self,
        mock_post,
        model,
        prompt_stack,
        use_native_tools,
        structured_output_strategy,
    ):
        # Given
        driver = GriptapeCloudPromptDriver(
            api_key="foo",
            model=model,
            stream=True,
            use_native_tools=use_native_tools,
            structured_output_strategy=structured_output_strategy,
            extra_params={"foo": "bar"},
        )

        # When
        stream = driver.try_stream(prompt_stack)
        event = next(stream)

        # Then
        mock_post.assert_called_once_with(
            "https://cloud.griptape.ai/api/chat/messages/stream",
            headers={"Authorization": f"Bearer {driver.api_key}"},
            json={
                "messages": prompt_stack.to_dict()["messages"],
                "tools": self.GRIPTAPE_CLOUD_TOOLS,
                "output_schema": self.GRIPTAPE_CLOUD_STRUCTURED_OUTPUT_SCHEMA,
                "driver_configuration": {
                    **({"model": model} if model else {}),
                    "max_tokens": driver.max_tokens,
                    "use_native_tools": use_native_tools,
                    "temperature": driver.temperature,
                    "structured_output_strategy": structured_output_strategy,
                    "extra_params": {"foo": "bar"},
                },
            },
            stream=True,
        )
        assert isinstance(event.content, TextDeltaMessageContent)
        assert event.content.text == "model-output"

        event = next(stream)
        assert isinstance(event.content, ActionCallDeltaMessageContent)
        assert event.content.index == 0
        assert event.content.tag == "MockTool_test"
        assert event.content.name == "MockTool"
        assert event.content.path == "test"
        assert event.content.partial_input == json.dumps({"foo": "bar"})

        event = next(stream)
        assert isinstance(event.content, ActionCallDeltaMessageContent)
        assert event.content.index == 1
        assert event.content.tag == "MockTool_test"
        assert event.content.name == "MockTool"
        assert event.content.path == "test"
        assert event.content.partial_input == json.dumps({"foo": "bar"})

        event = next(stream)
        assert isinstance(event.content, AudioDeltaMessageContent)
        assert event.content.data == "YXNzaXN0YW50LWF1ZGlvLWRhdGE="

        event = next(stream)
        assert isinstance(event.content, AudioDeltaMessageContent)
        assert event.content.expires_at == ANY
        assert event.content.transcript == "assistant-audio-transcription"

    @pytest.mark.parametrize("model", [None, "gpt-4.1"])
    @pytest.mark.parametrize("use_native_tools", [True, False])
    @pytest.mark.parametrize("structured_output_strategy", ["native", "tool", "rule", "foo"])
    def test_try_stream_run_error(
        self,
        mocker,
        model,
        prompt_stack,
        use_native_tools,
        structured_output_strategy,
    ):
        def request(*args, **kwargs):
            mock_response = mocker.Mock()
            if "chat/messages/stream" in args[0]:
                mock_response.iter_lines.return_value = [
                    f"data: {json.dumps(event)}".encode()
                    for event in [
                        {
                            "error": "A mocked error occurred",
                        }
                    ]
                ]

                mock_response.__enter__ = MagicMock(return_value=mock_response)
                mock_response.__exit__ = MagicMock()
                return mock_response
            return mocker.Mock(
                raise_for_status=lambda: None,
            )

        mock_post_stream_error = mocker.patch("requests.post", side_effect=request)

        # Given
        driver = GriptapeCloudPromptDriver(
            api_key="foo",
            model=model,
            stream=True,
            use_native_tools=use_native_tools,
            structured_output_strategy=structured_output_strategy,
            extra_params={"foo": "bar"},
        )

        # When
        stream = driver.try_stream(prompt_stack)
        with pytest.raises(StopIteration):
            next(stream)

        # Then
        mock_post_stream_error.assert_called_once_with(
            "https://cloud.griptape.ai/api/chat/messages/stream",
            headers={"Authorization": f"Bearer {driver.api_key}"},
            json={
                "messages": prompt_stack.to_dict()["messages"],
                "tools": self.GRIPTAPE_CLOUD_TOOLS,
                "output_schema": self.GRIPTAPE_CLOUD_STRUCTURED_OUTPUT_SCHEMA,
                "driver_configuration": {
                    **({"model": model} if model else {}),
                    "max_tokens": driver.max_tokens,
                    "use_native_tools": use_native_tools,
                    "temperature": driver.temperature,
                    "structured_output_strategy": structured_output_strategy,
                    "extra_params": {"foo": "bar"},
                },
            },
            stream=True,
        )
