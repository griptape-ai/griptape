from unittest.mock import MagicMock, Mock

import pytest
from google.generativeai.protos import FunctionCall, FunctionResponse, Part
from google.generativeai.types import ContentDict, GenerationConfig
from google.protobuf.json_format import MessageToDict

from griptape.artifacts import ActionArtifact, GenericArtifact, ImageArtifact, TextArtifact
from griptape.artifacts.list_artifact import ListArtifact
from griptape.common import ActionCallDeltaMessageContent, PromptStack, TextDeltaMessageContent, ToolAction
from griptape.drivers import GooglePromptDriver
from tests.mocks.mock_tool.tool import MockTool


class TestGooglePromptDriver:
    GOOGLE_TOOLS = [
        {
            "name": "MockTool_test",
            "description": "test description: foo",
            "parameters": {"type": "OBJECT", "properties": {"test": {"type": "STRING"}}, "required": ["test"]},
        },
        {
            "name": "MockTool_test_error",
            "description": "test description: foo",
            "parameters": {"type": "OBJECT", "properties": {"test": {"type": "STRING"}}, "required": ["test"]},
        },
        {
            "name": "MockTool_test_exception",
            "description": "test description: foo",
            "parameters": {"type": "OBJECT", "properties": {"test": {"type": "STRING"}}, "required": ["test"]},
        },
        {"name": "MockTool_test_list_output", "description": "test description"},
        {"name": "MockTool_test_no_schema", "description": "test description"},
        {
            "name": "MockTool_test_str_output",
            "description": "test description: foo",
            "parameters": {"type": "OBJECT", "properties": {"test": {"type": "STRING"}}, "required": ["test"]},
        },
        {
            "name": "MockTool_test_without_default_memory",
            "description": "test description",
            "parameters": {"type": "OBJECT", "properties": {"test": {"type": "STRING"}}, "required": ["test"]},
        },
    ]

    @pytest.fixture()
    def mock_generative_model(self, mocker):
        mock_generative_model = mocker.patch("google.generativeai.GenerativeModel")
        mocker.patch("google.protobuf.json_format.MessageToDict").return_value = {
            "args": {"foo": "bar"},
        }
        mock_function_call = MagicMock(
            type="tool_use", name="bar", id="MockTool_test", _pb=MagicMock(args={"foo": "bar"})
        )
        mock_function_call.name = "MockTool_test"
        mock_generative_model.return_value.generate_content.return_value = Mock(
            parts=[
                Mock(text="model-output", function_call=None),
                MagicMock(name="foo", text=None, function_call=mock_function_call),
            ],
            usage_metadata=MagicMock(prompt_token_count=5, candidates_token_count=10),
        )

        return mock_generative_model

    @pytest.fixture()
    def mock_stream_generative_model(self, mocker):
        mock_generative_model = mocker.patch("google.generativeai.GenerativeModel")
        mocker.patch("google.protobuf.json_format.MessageToDict").return_value = {
            "args": {"foo": "bar"},
        }
        mock_function_call_delta = MagicMock(
            type="tool_use", name="func call", id="MockTool_test", _pb=MagicMock(args={"foo": "bar"})
        )
        mock_function_call_delta.name = "MockTool_test"
        mock_generative_model.return_value.generate_content.return_value = iter(
            [
                MagicMock(
                    parts=[MagicMock(text="model-output")],
                    usage_metadata=MagicMock(prompt_token_count=5, candidates_token_count=5),
                ),
                MagicMock(
                    parts=[MagicMock(text=None, function_call=mock_function_call_delta)],
                    usage_metadata=MagicMock(prompt_token_count=5, candidates_token_count=5),
                ),
                MagicMock(
                    parts=[MagicMock(text="model-output", id="3")],
                    usage_metadata=MagicMock(prompt_token_count=5, candidates_token_count=5),
                ),
            ]
        )

        return mock_generative_model

    @pytest.fixture(params=[True, False])
    def prompt_stack(self, request):
        prompt_stack = PromptStack()
        prompt_stack.tools = [MockTool()]
        if request.param:
            prompt_stack.add_system_message("system-input")
        prompt_stack.add_user_message("user-input")
        prompt_stack.add_user_message(TextArtifact("user-input"))
        prompt_stack.add_user_message(ImageArtifact(value=b"image-data", format="png", width=100, height=100))
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
                            output=TextArtifact("tool-output", id="output"),
                        )
                    ),
                    TextArtifact("keep-going"),
                ]
            )
        )
        prompt_stack.add_user_message(GenericArtifact("video-file"))

        return prompt_stack

    @pytest.fixture()
    def messages(self):
        return [
            {"parts": ["user-input"], "role": "user"},
            {"parts": ["user-input"], "role": "user"},
            {"parts": [{"data": b"image-data", "mime_type": "image/png"}], "role": "user"},
            {"parts": ["assistant-input"], "role": "model"},
            {
                "parts": ["thought", Part(function_call=FunctionCall(name="MockTool_test", args={"foo": "bar"}))],
                "role": "model",
            },
            {
                "parts": [
                    Part(
                        function_response=FunctionResponse(
                            name="MockTool_test", response=TextArtifact("tool-output", id="output").to_dict()
                        )
                    ),
                    "keep-going",
                ],
                "role": "user",
            },
            {"parts": ["video-file"], "role": "user"},
        ]

    def test_init(self):
        driver = GooglePromptDriver(model="gemini-pro", api_key="1234")
        assert driver

    @pytest.mark.parametrize("use_native_tools", [True, False])
    def test_try_run(self, mock_generative_model, prompt_stack, messages, use_native_tools):
        # Given
        driver = GooglePromptDriver(
            model="gemini-pro", api_key="api-key", top_p=0.5, top_k=50, use_native_tools=use_native_tools
        )

        # When
        message = driver.try_run(prompt_stack)

        # Then
        if prompt_stack.system_messages:
            assert mock_generative_model.return_value._system_instruction == ContentDict(
                role="system", parts=[Part(text="system-input")]
            )
        mock_generative_model.return_value.generate_content.assert_called_once()
        # We can't use assert_called_once_with because we can't compare the FunctionDeclaration objects
        call_args = mock_generative_model.return_value.generate_content.call_args
        assert messages == call_args.args[0]
        generation_config = call_args.kwargs["generation_config"]
        assert generation_config == GenerationConfig(temperature=0.1, top_p=0.5, top_k=50, stop_sequences=[])
        if use_native_tools:
            tool_declarations = call_args.kwargs["tools"]
            assert [
                MessageToDict(tool_declaration.to_proto()._pb) for tool_declaration in tool_declarations
            ] == self.GOOGLE_TOOLS

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
    def test_try_stream(self, mock_stream_generative_model, prompt_stack, messages, use_native_tools):
        # Given
        driver = GooglePromptDriver(
            model="gemini-pro", api_key="api-key", stream=True, top_p=0.5, top_k=50, use_native_tools=use_native_tools
        )

        # When
        stream = driver.try_stream(prompt_stack)

        # Then
        event = next(stream)
        if prompt_stack.system_messages:
            assert mock_stream_generative_model.return_value._system_instruction == ContentDict(
                role="system", parts=[Part(text="system-input")]
            )
        # We can't use assert_called_once_with because we can't compare the FunctionDeclaration objects
        mock_stream_generative_model.return_value.generate_content.assert_called_once()
        call_args = mock_stream_generative_model.return_value.generate_content.call_args

        assert messages == call_args.args[0]
        assert call_args.kwargs["stream"] is True
        assert call_args.kwargs["generation_config"] == GenerationConfig(
            temperature=0.1, top_p=0.5, top_k=50, stop_sequences=[]
        )
        if use_native_tools:
            tool_declarations = call_args.kwargs["tools"]
            assert [
                MessageToDict(tool_declaration.to_proto()._pb) for tool_declaration in tool_declarations
            ] == self.GOOGLE_TOOLS
        assert isinstance(event.content, TextDeltaMessageContent)
        assert event.content.text == "model-output"
        assert event.usage.input_tokens == 5
        assert event.usage.output_tokens == 5

        event = next(stream)
        assert isinstance(event.content, ActionCallDeltaMessageContent)
        assert event.content.tag == "MockTool_test"
        assert event.content.name == "MockTool"
        assert event.content.path == "test"
        assert event.content.partial_input == '{"foo": "bar"}'

        event = next(stream)
        assert event.usage.output_tokens == 5
