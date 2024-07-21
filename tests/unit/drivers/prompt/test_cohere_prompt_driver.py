from unittest.mock import Mock

import pytest

from griptape.artifacts.action_artifact import ActionArtifact
from griptape.artifacts.list_artifact import ListArtifact
from griptape.artifacts.text_artifact import TextArtifact
from griptape.common import ActionCallDeltaMessageContent, PromptStack, TextDeltaMessageContent, ToolAction
from griptape.drivers import CoherePromptDriver
from tests.mocks.mock_tool.tool import MockTool


class TestCoherePromptDriver:
    COHERE_TOOLS = [
        {
            "description": "test description: foo",
            "name": "MockTool_test",
            "parameter_definitions": {"test": {"required": True, "type": "string"}},
        },
        {
            "description": "test description: foo",
            "name": "MockTool_test_error",
            "parameter_definitions": {"test": {"required": True, "type": "string"}},
        },
        {
            "description": "test description: foo",
            "name": "MockTool_test_exception",
            "parameter_definitions": {"test": {"required": True, "type": "string"}},
        },
        {"description": "test description", "name": "MockTool_test_list_output", "parameter_definitions": {}},
        {"description": "test description", "name": "MockTool_test_no_schema", "parameter_definitions": {}},
        {
            "description": "test description: foo",
            "name": "MockTool_test_str_output",
            "parameter_definitions": {"test": {"required": True, "type": "string"}},
        },
        {
            "description": "test description",
            "name": "MockTool_test_without_default_memory",
            "parameter_definitions": {"test": {"required": True, "type": "string"}},
        },
    ]

    @pytest.fixture()
    def mock_client(self, mocker):
        mock_client = mocker.patch("cohere.Client").return_value
        mock_tool_call = Mock(parameters={"foo": "bar"})
        mock_tool_call.name = "MockTool_test"
        mock_client.chat.return_value = Mock(
            text="model-output", meta=Mock(tokens=Mock(input_tokens=5, output_tokens=10)), tool_calls=[mock_tool_call]
        )

        return mock_client

    @pytest.fixture()
    def mock_stream_client(self, mocker):
        mock_client = mocker.patch("cohere.Client").return_value
        mock_tool_call_delta_header = Mock()
        mock_tool_call_delta_header.name = "MockTool_test"
        mock_tool_call_delta_body = Mock()
        mock_tool_call_delta_body.name = None
        mock_tool_call_delta_body.parameters = '{"foo": "bar"}'
        mock_client.chat_stream.return_value = iter(
            [
                Mock(text="model-output", event_type="text-generation"),
                Mock(text="model-output", event_type="tool-calls-chunk", tool_call_delta=mock_tool_call_delta_header),
                Mock(text="model-output", event_type="tool-calls-chunk", tool_call_delta=mock_tool_call_delta_body),
                Mock(response=Mock(meta=Mock(tokens=Mock(input_tokens=5, output_tokens=10))), event_type="stream-end"),
            ]
        )

        return mock_client

    @pytest.fixture(autouse=True)
    def mock_tokenizer(self, mocker):
        return mocker.patch("griptape.tokenizers.CohereTokenizer").return_value

    @pytest.fixture(params=[True, False])
    def prompt_stack(self, request):
        prompt_stack = PromptStack()
        prompt_stack.tools = [MockTool()]
        if request.param:
            prompt_stack.add_system_message("system-input")
        prompt_stack.add_user_message("user-input")
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
                    TextArtifact("keep going"),
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
            ListArtifact(
                [
                    TextArtifact("keep going"),
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
        assert CoherePromptDriver(model="command", api_key="foobar")

    @pytest.mark.parametrize("use_native_tools", [True, False])
    def test_try_run(self, mock_client, prompt_stack, use_native_tools):
        # Given
        driver = CoherePromptDriver(model="command", api_key="api-key", use_native_tools=use_native_tools)

        # When
        message = driver.try_run(prompt_stack)

        # Then
        mock_client.chat.assert_called_once_with(
            chat_history=[
                {"message": "user-input", "role": "USER"},
                {"message": "assistant-input", "role": "CHATBOT"},
                {
                    "message": "thought",
                    "role": "CHATBOT",
                    "tool_calls": [{"name": "MockTool_test", "parameters": {"foo": "bar"}}],
                },
                {
                    "message": "keep going",
                    "role": "TOOL",
                    "tool_results": [
                        {
                            "call": {"name": "MockTool_test", "parameters": {"foo": "bar"}},
                            "outputs": [{"text": "tool-output"}],
                        }
                    ],
                },
            ],
            max_tokens=None,
            message="keep going",
            **({"tools": self.COHERE_TOOLS, "force_single_step": False} if use_native_tools else {}),
            **({"preamble": "system-input"} if prompt_stack.system_messages else {}),
            tool_results=[
                {"call": {"name": "MockTool_test", "parameters": {"foo": "bar"}}, "outputs": [{"text": "tool-output"}]}
            ],
            stop_sequences=[],
            temperature=0.1,
        )

        assert isinstance(message.value[0], TextArtifact)
        assert message.value[0].value == "model-output"
        assert isinstance(message.value[1], ActionArtifact)
        assert message.value[1].value.tag == "MockTool_test"
        assert message.value[1].value.name == "MockTool"
        assert message.value[1].value.path == "test"
        assert message.value[1].value.input == {"foo": "bar"}

        assert message.usage.input_tokens == 5
        assert message.usage.output_tokens == 10

    @pytest.mark.parametrize("use_native_tools", [True, False])
    def test_try_stream_run(self, mock_stream_client, prompt_stack, use_native_tools):
        # Given
        driver = CoherePromptDriver(model="command", api_key="api-key", stream=True, use_native_tools=use_native_tools)

        # When
        stream = driver.try_stream(prompt_stack)
        event = next(stream)

        # Then
        mock_stream_client.chat_stream.assert_called_once_with(
            chat_history=[
                {"message": "user-input", "role": "USER"},
                {"message": "assistant-input", "role": "CHATBOT"},
                {
                    "message": "thought",
                    "role": "CHATBOT",
                    "tool_calls": [{"name": "MockTool_test", "parameters": {"foo": "bar"}}],
                },
                {
                    "role": "TOOL",
                    "message": "keep going",
                    "tool_results": [
                        {
                            "call": {"name": "MockTool_test", "parameters": {"foo": "bar"}},
                            "outputs": [{"text": "tool-output"}],
                        }
                    ],
                },
            ],
            max_tokens=None,
            message="keep going",
            **({"tools": self.COHERE_TOOLS, "force_single_step": False} if use_native_tools else {}),
            **({"preamble": "system-input"} if prompt_stack.system_messages else {}),
            tool_results=[
                {"call": {"name": "MockTool_test", "parameters": {"foo": "bar"}}, "outputs": [{"text": "tool-output"}]}
            ],
            stop_sequences=[],
            temperature=0.1,
        )

        assert isinstance(event.content, TextDeltaMessageContent)
        assert event.content.text == "model-output"

        event = next(stream)
        assert isinstance(event.content, ActionCallDeltaMessageContent)
        assert event.content.tag == "MockTool_test"
        assert event.content.name == "MockTool"
        assert event.content.path == "test"

        event = next(stream)
        assert isinstance(event.content, ActionCallDeltaMessageContent)
        assert event.content.partial_input == '{"foo": "bar"}'

        event = next(stream)
        assert event.usage.input_tokens == 5
        assert event.usage.output_tokens == 10
