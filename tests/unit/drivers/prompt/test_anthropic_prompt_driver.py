from unittest.mock import Mock

import pytest

from griptape.artifacts import ActionArtifact, ImageArtifact, ListArtifact, TextArtifact
from griptape.artifacts.error_artifact import ErrorArtifact
from griptape.common import ActionCallDeltaMessageContent, PromptStack, TextDeltaMessageContent, ToolAction
from griptape.drivers import AnthropicPromptDriver
from tests.mocks.mock_tool.tool import MockTool


class TestAnthropicPromptDriver:
    ANTHROPIC_TOOLS = [
        {
            "description": "test description: foo",
            "input_schema": {
                "$id": "Input Schema",
                "$schema": "http://json-schema.org/draft-07/schema#",
                "additionalProperties": False,
                "properties": {
                    "values": {
                        "additionalProperties": False,
                        "description": "Test input",
                        "properties": {"test": {"type": "string"}},
                        "required": ["test"],
                        "type": "object",
                    }
                },
                "required": ["values"],
                "type": "object",
            },
            "name": "MockTool_test",
        },
        {
            "description": "test description: foo",
            "input_schema": {
                "$id": "Input Schema",
                "$schema": "http://json-schema.org/draft-07/schema#",
                "additionalProperties": False,
                "properties": {
                    "values": {
                        "additionalProperties": False,
                        "description": "Test input",
                        "properties": {"test": {"type": "string"}},
                        "required": ["test"],
                        "type": "object",
                    }
                },
                "required": ["values"],
                "type": "object",
            },
            "name": "MockTool_test_error",
        },
        {
            "description": "test description: foo",
            "input_schema": {
                "$id": "Input Schema",
                "$schema": "http://json-schema.org/draft-07/schema#",
                "additionalProperties": False,
                "properties": {
                    "values": {
                        "additionalProperties": False,
                        "description": "Test input",
                        "properties": {"test": {"type": "string"}},
                        "required": ["test"],
                        "type": "object",
                    }
                },
                "required": ["values"],
                "type": "object",
            },
            "name": "MockTool_test_exception",
        },
        {
            "description": "test description",
            "input_schema": {
                "$id": "Input Schema",
                "$schema": "http://json-schema.org/draft-07/schema#",
                "additionalProperties": False,
                "properties": {},
                "required": [],
                "type": "object",
            },
            "name": "MockTool_test_list_output",
        },
        {
            "description": "test description",
            "input_schema": {
                "$id": "Input Schema",
                "$schema": "http://json-schema.org/draft-07/schema#",
                "additionalProperties": False,
                "properties": {},
                "required": [],
                "type": "object",
            },
            "name": "MockTool_test_no_schema",
        },
        {
            "description": "test description: foo",
            "input_schema": {
                "$id": "Input Schema",
                "$schema": "http://json-schema.org/draft-07/schema#",
                "additionalProperties": False,
                "properties": {
                    "values": {
                        "additionalProperties": False,
                        "description": "Test input",
                        "properties": {"test": {"type": "string"}},
                        "required": ["test"],
                        "type": "object",
                    }
                },
                "required": ["values"],
                "type": "object",
            },
            "name": "MockTool_test_str_output",
        },
        {
            "description": "test description",
            "input_schema": {
                "$id": "Input Schema",
                "$schema": "http://json-schema.org/draft-07/schema#",
                "additionalProperties": False,
                "properties": {
                    "values": {
                        "additionalProperties": False,
                        "description": "Test input",
                        "properties": {"test": {"type": "string"}},
                        "required": ["test"],
                        "type": "object",
                    }
                },
                "required": ["values"],
                "type": "object",
            },
            "name": "MockTool_test_without_default_memory",
        },
    ]

    @pytest.fixture()
    def mock_client(self, mocker):
        mock_client = mocker.patch("anthropic.Anthropic")
        mock_tool_use = Mock(type="tool_use", id="mock-id", input={"foo": "bar"})
        mock_tool_use.name = "MockTool_test"

        mock_client.return_value = Mock(
            messages=Mock(
                create=Mock(
                    return_value=Mock(
                        usage=Mock(input_tokens=5, output_tokens=10),
                        content=[Mock(type="text", text="model-output"), mock_tool_use],
                    )
                )
            )
        )

        return mock_client

    @pytest.fixture()
    def mock_stream_client(self, mocker):
        mock_stream_client = mocker.patch("anthropic.Anthropic")

        mock_tool_call_delta_header = Mock(type="tool_use", id="mock-id")
        mock_tool_call_delta_header.name = "MockTool_test"

        mock_stream_client.return_value = Mock(
            messages=Mock(
                create=Mock(
                    return_value=iter(
                        [
                            Mock(type="message_start", message=Mock(usage=Mock(input_tokens=5))),
                            Mock(
                                type="content_block_start",
                                index=0,
                                content_block=Mock(type="text", text="model-output"),
                            ),
                            Mock(
                                type="content_block_delta", index=0, delta=Mock(type="text_delta", text="model-output")
                            ),
                            Mock(type="content_block_start", index=1, content_block=mock_tool_call_delta_header),
                            Mock(
                                type="content_block_delta",
                                index=1,
                                delta=Mock(type="input_json_delta", partial_json='{"foo": "bar"}'),
                            ),
                            Mock(type="message_delta", usage=Mock(output_tokens=10)),
                        ]
                    )
                )
            )
        )

        return mock_stream_client

    @pytest.fixture(params=[True, False])
    def prompt_stack(self, request):
        prompt_stack = PromptStack()
        prompt_stack.tools = [MockTool()]
        if request.param:
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
                    TextArtifact("thought"),
                    ActionArtifact(ToolAction(tag="MockTool_test", name="MockTool", path="test", input={"foo": "bar"})),
                ]
            )
        )
        prompt_stack.add_user_message(
            ListArtifact(
                [
                    ActionArtifact(
                        ToolAction(
                            tag="MockTool_test",
                            name="MockTool",
                            path="test",
                            input={"foo": "bar"},
                            output=TextArtifact("tool-output"),
                        )
                    ),
                    TextArtifact("keep-going"),
                ]
            )
        )
        prompt_stack.add_user_message(
            ListArtifact(
                [
                    ActionArtifact(
                        ToolAction(
                            tag="MockTool_test",
                            name="MockTool",
                            path="test",
                            input={"foo": "bar"},
                            output=ListArtifact(
                                [
                                    TextArtifact("tool-output"),
                                    ImageArtifact(value=b"image-data", format="png", width=100, height=100),
                                ]
                            ),
                        )
                    ),
                    TextArtifact("keep-going"),
                ]
            )
        )
        prompt_stack.add_user_message(
            ListArtifact(
                [
                    ActionArtifact(
                        ToolAction(
                            tag="MockTool_test",
                            name="MockTool",
                            path="test",
                            input={"foo": "bar"},
                            output=ErrorArtifact("error"),
                        )
                    ),
                    TextArtifact("keep-going"),
                ]
            )
        )

        return prompt_stack

    @pytest.fixture()
    def messages(self):
        return [
            {"role": "user", "content": "user-input"},
            {
                "content": [
                    {"type": "text", "text": "user-input"},
                    {
                        "source": {"data": "aW1hZ2UtZGF0YQ==", "media_type": "image/png", "type": "base64"},
                        "type": "image",
                    },
                ],
                "role": "user",
            },
            {"role": "assistant", "content": "assistant-input"},
            {
                "content": [
                    {"text": "thought", "type": "text"},
                    {"id": "MockTool_test", "input": {"foo": "bar"}, "name": "MockTool_test", "type": "tool_use"},
                ],
                "role": "assistant",
            },
            {
                "content": [
                    {
                        "content": [{"text": "tool-output", "type": "text"}],
                        "is_error": False,
                        "tool_use_id": "MockTool_test",
                        "type": "tool_result",
                    },
                    {"text": "keep-going", "type": "text"},
                ],
                "role": "user",
            },
            {
                "content": [
                    {
                        "content": [
                            {"text": "tool-output", "type": "text"},
                            {
                                "source": {"data": "aW1hZ2UtZGF0YQ==", "media_type": "image/png", "type": "base64"},
                                "type": "image",
                            },
                        ],
                        "is_error": False,
                        "tool_use_id": "MockTool_test",
                        "type": "tool_result",
                    },
                    {"text": "keep-going", "type": "text"},
                ],
                "role": "user",
            },
            {
                "content": [
                    {
                        "content": [{"text": "error", "type": "text"}],
                        "is_error": True,
                        "tool_use_id": "MockTool_test",
                        "type": "tool_result",
                    },
                    {"text": "keep-going", "type": "text"},
                ],
                "role": "user",
            },
        ]

    def test_init(self):
        assert AnthropicPromptDriver(model="claude-3-haiku", api_key="1234")

    @pytest.mark.parametrize("use_native_tools", [True, False])
    def test_try_run(self, mock_client, prompt_stack, messages, use_native_tools):
        # Given
        driver = AnthropicPromptDriver(model="claude-3-haiku", api_key="api-key", use_native_tools=use_native_tools)

        # When
        message = driver.try_run(prompt_stack)

        # Then
        mock_client.return_value.messages.create.assert_called_once_with(
            messages=messages,
            stop_sequences=[],
            model=driver.model,
            max_tokens=1000,
            temperature=0.1,
            top_p=0.999,
            top_k=250,
            **{"system": "system-input"} if prompt_stack.system_messages else {},
            **{"tools": self.ANTHROPIC_TOOLS, "tool_choice": driver.tool_choice} if use_native_tools else {},
        )
        assert isinstance(message.value[0], TextArtifact)
        assert message.value[0].value == "model-output"
        assert isinstance(message.value[1], ActionArtifact)
        assert message.value[1].value.tag == "mock-id"
        assert message.value[1].value.name == "MockTool"
        assert message.value[1].value.path == "test"
        assert message.value[1].value.input == {"foo": "bar"}
        assert message.usage.input_tokens == 5
        assert message.usage.output_tokens == 10

    @pytest.mark.parametrize("use_native_tools", [True, False])
    def test_try_stream_run(self, mock_stream_client, prompt_stack, messages, use_native_tools):
        # Given
        driver = AnthropicPromptDriver(
            model="claude-3-haiku", api_key="api-key", stream=True, use_native_tools=use_native_tools
        )

        # When
        stream = driver.try_stream(prompt_stack)
        event = next(stream)

        # Then
        mock_stream_client.return_value.messages.create.assert_called_once_with(
            messages=messages,
            stop_sequences=[],
            model=driver.model,
            max_tokens=1000,
            temperature=0.1,
            stream=True,
            top_p=0.999,
            top_k=250,
            **{"system": "system-input"} if prompt_stack.system_messages else {},
            **{"tools": self.ANTHROPIC_TOOLS, "tool_choice": driver.tool_choice} if use_native_tools else {},
        )
        assert event.usage.input_tokens == 5

        event = next(stream)
        assert isinstance(event.content, TextDeltaMessageContent)
        assert event.content.text == "model-output"

        event = next(stream)
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
        assert event.usage.output_tokens == 10
