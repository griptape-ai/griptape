from unittest.mock import Mock

import pytest

from griptape.artifacts import ActionArtifact, TextArtifact
from griptape.common import ActionCallDeltaMessageContent, TextDeltaMessageContent
from griptape.drivers import AzureOpenAiChatPromptDriver
from tests.unit.drivers.prompt.test_openai_chat_prompt_driver import TestOpenAiChatPromptDriverFixtureMixin


class TestAzureOpenAiChatPromptDriver(TestOpenAiChatPromptDriverFixtureMixin):
    @pytest.fixture()
    def mock_chat_completion_create(self, mocker):
        mock_chat_create = mocker.patch("openai.AzureOpenAI").return_value.chat.completions.create
        mock_function = Mock(arguments='{"foo": "bar"}', id="mock-id")
        mock_function.name = "MockTool_test"
        mock_chat_create.return_value = Mock(
            headers={},
            choices=[
                Mock(message=Mock(content="model-output", tool_calls=[Mock(id="mock-id", function=mock_function)]))
            ],
            usage=Mock(prompt_tokens=5, completion_tokens=10),
        )

        return mock_chat_create

    @pytest.fixture()
    def mock_chat_completion_stream_create(self, mocker):
        mock_chat_create = mocker.patch("openai.AzureOpenAI").return_value.chat.completions.create
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
                Mock(choices=[Mock(delta=Mock(content=None, tool_calls=None))], usage=None),
            ]
        )
        return mock_chat_create

    def test_init(self):
        assert AzureOpenAiChatPromptDriver(azure_endpoint="foobar", azure_deployment="foobar", model="gpt-4")
        assert AzureOpenAiChatPromptDriver(azure_endpoint="foobar", model="gpt-4").azure_deployment == "gpt-4"

    @pytest.mark.parametrize("use_native_tools", [True, False])
    def test_try_run(self, mock_chat_completion_create, prompt_stack, messages, use_native_tools):
        # Given
        driver = AzureOpenAiChatPromptDriver(
            azure_endpoint="endpoint",
            azure_deployment="deployment-id",
            model="gpt-4",
            use_native_tools=use_native_tools,
        )

        # When
        message = driver.try_run(prompt_stack)

        # Then
        mock_chat_completion_create.assert_called_once_with(
            model=driver.model,
            temperature=driver.temperature,
            user=driver.user,
            messages=messages,
            **{"tools": self.OPENAI_TOOLS, "tool_choice": driver.tool_choice} if use_native_tools else {},
        )
        assert isinstance(message.value[0], TextArtifact)
        assert message.value[0].value == "model-output"
        assert isinstance(message.value[1], ActionArtifact)
        assert message.value[1].value.tag == "mock-id"
        assert message.value[1].value.name == "MockTool"
        assert message.value[1].value.path == "test"
        assert message.value[1].value.input == {"foo": "bar"}

    @pytest.mark.parametrize("use_native_tools", [True, False])
    def test_try_stream_run(self, mock_chat_completion_stream_create, prompt_stack, messages, use_native_tools):
        # Given
        driver = AzureOpenAiChatPromptDriver(
            azure_endpoint="endpoint",
            azure_deployment="deployment-id",
            model="gpt-4",
            stream=True,
            use_native_tools=use_native_tools,
        )

        # When
        stream = driver.try_stream(prompt_stack)
        event = next(stream)

        # Then
        mock_chat_completion_stream_create.assert_called_once_with(
            model=driver.model,
            temperature=driver.temperature,
            user=driver.user,
            stream=True,
            messages=messages,
            **{"tools": self.OPENAI_TOOLS, "tool_choice": driver.tool_choice} if use_native_tools else {},
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
        assert isinstance(event.content, TextDeltaMessageContent)
        assert event.content.text == ""
