from unittest.mock import MagicMock, Mock

import pytest
from google.genai.types import (
    Content,
    FunctionCall,
    FunctionCallingConfig,
    FunctionResponse,
    GenerateContentConfig,
    Part,
    ToolConfig,
)
from schema import Schema

from griptape.artifacts import ActionArtifact, GenericArtifact, ImageArtifact, TextArtifact
from griptape.artifacts.list_artifact import ListArtifact
from griptape.common import ActionCallDeltaMessageContent, PromptStack, TextDeltaMessageContent, ToolAction
from griptape.drivers.prompt.google import GooglePromptDriver
from tests.mocks.mock_tool.tool import MockTool


class TestGooglePromptDriver:
    GOOGLE_TOOLS = [
        {
            "name": "MockTool_test",
            "description": "test description: foo",
            "parameters": {"type": "OBJECT", "properties": {"test": {"type": "STRING"}}, "required": ["test"]},
        },
        {
            "name": "MockTool_test_callable_schema",
            "description": "test description",
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
    def mock_client(self, mocker):
        mock_client = mocker.patch("google.genai.Client")
        mock_function_call = MagicMock(args={"foo": "bar"})
        mock_function_call.name = "MockTool_test"
        mock_text_part = MagicMock(text="model-output", function_call=None)
        mock_function_call_part = MagicMock(text=None, function_call=mock_function_call)
        mock_candidate = MagicMock(content=MagicMock(parts=[mock_text_part, mock_function_call_part]))
        mock_client.return_value.models.generate_content.return_value = Mock(
            candidates=[mock_candidate],
            usage_metadata=MagicMock(prompt_token_count=5, candidates_token_count=10),
        )

        return mock_client

    @pytest.fixture()
    def mock_stream_client(self, mocker):
        mock_client = mocker.patch("google.genai.Client")
        mock_function_call_delta = MagicMock(args={"foo": "bar"})
        mock_function_call_delta.name = "MockTool_test"

        def make_chunk(*, text, function_call):
            part = MagicMock(text=text, function_call=function_call)
            candidate = MagicMock(content=MagicMock(parts=[part]))
            return MagicMock(
                candidates=[candidate],
                usage_metadata=MagicMock(prompt_token_count=5, candidates_token_count=5),
            )

        mock_client.return_value.models.generate_content_stream.return_value = iter(
            [
                make_chunk(text="model-output", function_call=None),
                make_chunk(text=None, function_call=mock_function_call_delta),
                make_chunk(text="model-output", function_call=None),
            ]
        )

        return mock_client

    @pytest.fixture(params=[True, False])
    def prompt_stack(self, request):
        prompt_stack = PromptStack()
        prompt_stack.output_schema = Schema({"foo": str})
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
            Content(role="user", parts=[Part.from_text(text="user-input")]),
            Content(role="user", parts=[Part.from_text(text="user-input")]),
            Content(role="user", parts=[Part.from_bytes(data=b"image-data", mime_type="image/png")]),
            Content(role="model", parts=[Part.from_text(text="assistant-input")]),
            Content(
                role="model",
                parts=[
                    Part.from_text(text="thought"),
                    Part(function_call=FunctionCall(name="MockTool_test", args={"foo": "bar"})),
                ],
            ),
            Content(
                role="user",
                parts=[
                    Part(
                        function_response=FunctionResponse(
                            name="MockTool_test", response=TextArtifact("tool-output", id="output").to_dict()
                        )
                    ),
                    Part.from_text(text="keep-going"),
                ],
            ),
            Content(role="user", parts=[Part.from_text(text="video-file")]),
        ]

    def test_init(self):
        driver = GooglePromptDriver(model="gemini-2.0-flash", api_key="1234")
        assert driver

    @pytest.mark.parametrize("use_native_tools", [True, False])
    @pytest.mark.parametrize("structured_output_strategy", ["native", "tool", "rule", "foo"])
    def test_try_run(self, mock_client, prompt_stack, messages, use_native_tools, structured_output_strategy):
        # Given
        driver = GooglePromptDriver(
            model="gemini-2.0-flash",
            api_key="api-key",
            top_p=0.5,
            top_k=50,
            use_native_tools=use_native_tools,
            structured_output_strategy=structured_output_strategy,
            extra_params={"max_output_tokens": 10},
        )

        # When
        message = driver.try_run(prompt_stack)

        # Then
        mock_client.return_value.models.generate_content.assert_called_once()
        call_args = mock_client.return_value.models.generate_content.call_args
        assert call_args.kwargs["model"] == "gemini-2.0-flash"
        assert messages == call_args.kwargs["contents"]
        config = call_args.kwargs["config"]
        assert isinstance(config, GenerateContentConfig)
        assert config.temperature == 0.1
        assert config.top_p == 0.5
        assert config.top_k == 50
        assert config.stop_sequences == []
        assert config.max_output_tokens == 10
        if prompt_stack.system_messages:
            assert config.system_instruction == Content(role="system", parts=[Part.from_text(text="system-input")])
        else:
            assert config.system_instruction is None
        if use_native_tools:
            tools = config.tools
            assert len(tools) == 1
            declarations = [declaration.model_dump(exclude_none=True) for declaration in tools[0].function_declarations]
            assert declarations == self.GOOGLE_TOOLS

            if driver.structured_output_strategy == "tool":
                assert config.tool_config == ToolConfig(
                    function_calling_config=FunctionCallingConfig(mode="AUTO"),
                )

        if driver.structured_output_strategy == "native":
            assert config.response_mime_type == "application/json"
            assert config.response_json_schema == prompt_stack.to_output_json_schema()
        else:
            assert config.response_mime_type is None
            assert config.response_json_schema is None

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
    @pytest.mark.parametrize("structured_output_strategy", ["native", "tool", "rule", "foo"])
    def test_try_stream(self, mock_stream_client, prompt_stack, messages, use_native_tools, structured_output_strategy):
        # Given
        driver = GooglePromptDriver(
            model="gemini-2.0-flash",
            api_key="api-key",
            stream=True,
            top_p=0.5,
            top_k=50,
            use_native_tools=use_native_tools,
            structured_output_strategy=structured_output_strategy,
            extra_params={"max_output_tokens": 10},
        )

        # When
        stream = driver.try_stream(prompt_stack)

        # Then
        event = next(stream)
        mock_stream_client.return_value.models.generate_content_stream.assert_called_once()
        call_args = mock_stream_client.return_value.models.generate_content_stream.call_args

        assert call_args.kwargs["model"] == "gemini-2.0-flash"
        assert messages == call_args.kwargs["contents"]
        config = call_args.kwargs["config"]
        assert isinstance(config, GenerateContentConfig)
        assert config.temperature == 0.1
        assert config.top_p == 0.5
        assert config.top_k == 50
        assert config.stop_sequences == []
        assert config.max_output_tokens == 10
        if use_native_tools:
            tools = config.tools
            assert len(tools) == 1
            declarations = [declaration.model_dump(exclude_none=True) for declaration in tools[0].function_declarations]
            assert declarations == self.GOOGLE_TOOLS

            if driver.structured_output_strategy == "tool":
                assert config.tool_config == ToolConfig(
                    function_calling_config=FunctionCallingConfig(mode="AUTO"),
                )

        if driver.structured_output_strategy == "native":
            assert config.response_mime_type == "application/json"
            assert config.response_json_schema == prompt_stack.to_output_json_schema()
        else:
            assert config.response_mime_type is None
            assert config.response_json_schema is None

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

    def test_try_run_skips_thought_parts(self, mocker):
        """Skip reasoning-only parts emitted by Gemini thinking models.

        Such parts carry only a `thought_signature`; they must not appear in `Message.content`
        and must not raise on conversion.
        """
        # Given
        mock_client = mocker.patch("google.genai.Client")
        mock_text_part = MagicMock(text="model-output", function_call=None, thought=None, thought_signature=None)
        mock_thought_part = MagicMock(text="", function_call=None, thought=None, thought_signature=b"sig-bytes")
        mock_candidate = MagicMock(content=MagicMock(parts=[mock_thought_part, mock_text_part]))
        mock_client.return_value.models.generate_content.return_value = Mock(
            candidates=[mock_candidate],
            usage_metadata=MagicMock(prompt_token_count=5, candidates_token_count=10),
        )
        driver = GooglePromptDriver(model="gemini-3-pro", api_key="api-key")

        # When
        message = driver.try_run(PromptStack())

        # Then
        assert len(message.content) == 1
        assert message.content[0].artifact.value == "model-output"

    def test_try_stream_skips_thought_chunks(self, mocker):
        """A chunk whose only part is thought-only should yield `content=None` rather than raise."""
        # Given
        mock_client = mocker.patch("google.genai.Client")

        def make_chunk(*, text, thought_signature):
            part = MagicMock(text=text, function_call=None, thought=None, thought_signature=thought_signature)
            candidate = MagicMock(content=MagicMock(parts=[part]))
            return MagicMock(
                candidates=[candidate],
                usage_metadata=MagicMock(prompt_token_count=5, candidates_token_count=5),
            )

        mock_client.return_value.models.generate_content_stream.return_value = iter(
            [
                make_chunk(text="", thought_signature=b"sig-bytes"),
                make_chunk(text="model-output", thought_signature=None),
            ]
        )
        driver = GooglePromptDriver(model="gemini-3-pro", api_key="api-key", stream=True)

        # When
        events = list(driver.try_stream(PromptStack()))

        # Then
        assert len(events) == 2
        assert events[0].content is None
        assert isinstance(events[1].content, TextDeltaMessageContent)
        assert events[1].content.text == "model-output"
