import json
from griptape.artifacts.action_chunk_artifact import ActionChunkArtifact
from griptape.artifacts.actions_artifact import ActionsArtifact
from griptape.artifacts.text_artifact import TextArtifact
from griptape.drivers import AnthropicPromptDriver
from griptape.utils import PromptStack
from unittest.mock import Mock
import pytest

from tests.unit.drivers.prompt.test_openai_chat_prompt_driver import MockTool


class TestAnthropicPromptDriver:
    TOOLS_SCHEMA = [
        {
            "description": "test description: foo",
            "input_schema": {
                "$id": "Input Schema",
                "$schema": "http://json-schema.org/draft-07/schema#",
                "additionalProperties": False,
                "properties": {
                    "values": {
                        "additionalProperties": False,
                        "properties": {"test": {"type": "string"}},
                        "required": ["test"],
                        "type": "object",
                    }
                },
                "required": ["values"],
                "type": "object",
            },
            "name": "MockTool-test",
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
                        "properties": {"test": {"type": "string"}},
                        "required": ["test"],
                        "type": "object",
                    }
                },
                "required": ["values"],
                "type": "object",
            },
            "name": "MockTool-test_error",
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
            "name": "MockTool-test_list_output",
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
            "name": "MockTool-test_no_schema",
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
                        "properties": {"test": {"type": "string"}},
                        "required": ["test"],
                        "type": "object",
                    }
                },
                "required": ["values"],
                "type": "object",
            },
            "name": "MockTool-test_str_output",
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
                        "properties": {"test": {"type": "string"}},
                        "required": ["test"],
                        "type": "object",
                    }
                },
                "required": ["values"],
                "type": "object",
            },
            "name": "MockTool-test_without_default_memory",
        },
    ]

    @pytest.fixture
    def mock_client(self, mocker):
        mock_client = mocker.patch("anthropic.Anthropic")
        mock_content = Mock()
        mock_content.type = "text"
        mock_content.text = "model-output"
        mock_client.return_value.beta.tools.messages.create.return_value.content = [mock_content]
        mock_client.return_value.count_tokens.return_value = 5

        return mock_client

    @pytest.fixture
    def mock_client_with_tools(self, mocker):
        mock_client = mocker.patch("anthropic.Anthropic")

        mock_content = Mock()
        mock_content.type = "text"
        mock_content.text = "model-output"

        mock_tool = Mock()
        mock_tool.type = "tool_use"
        mock_tool.id = "tool-call-id"
        mock_tool.name = "ToolName-ActivityName"
        mock_tool.input = {"values": {"test": "test input"}}

        mock_client.return_value.beta.tools.messages.create.return_value.content = [mock_content, mock_tool]
        mock_client.return_value.count_tokens.return_value = 5

        return mock_client

    @pytest.fixture
    def mock_stream_client(self, mocker):
        mock_stream_client = mocker.patch("anthropic.Anthropic")
        mock_chunk = Mock()
        mock_chunk.type = "content_block_delta"
        mock_chunk.delta.type = "text_delta"
        mock_chunk.delta.text = "model-output"
        mock_stream_client.return_value.beta.tools.messages.create.return_value = iter([mock_chunk])
        mock_stream_client.return_value.count_tokens.return_value = 5

        return mock_stream_client

    @pytest.fixture
    def mock_stream_client_with_tools(self, mocker):
        mock_stream_client = mocker.patch("anthropic.Anthropic")

        mock_chunks = [
            Mock(type="content_block_start", index=0, content_block=Mock(type="text", text="")),
            Mock(type="content_block_delta", index=0, delta=Mock(type="text_delta", text="thinking")),
            Mock(type="content_block_start", index=0, content_block=Mock(type="tool_use", id="tool-call-id")),
            Mock(type="content_block_delta", index=0, delta=Mock(type="input_json_delta", partial_json="tool-output")),
        ]
        # Name is a special Mock attribute that needs to be set after creation
        mock_chunks[2].content_block.name = "ToolName-ActivityName"

        mock_stream_client.return_value.beta.tools.messages.create.return_value = iter(mock_chunks)
        mock_stream_client.return_value.count_tokens.return_value = 5

        return mock_stream_client

    @pytest.mark.parametrize("model", [("claude-2.1"), ("claude-2.0")])
    def test_init(self, model):
        assert AnthropicPromptDriver(model=model, api_key="1234")

    @pytest.mark.parametrize(
        "model",
        [
            ("claude-instant-1.2"),
            ("claude-2.1"),
            ("claude-2.0"),
            ("claude-3-opus"),
            ("claude-3-sonnet"),
            ("claude-3-haiku"),
        ],
    )
    @pytest.mark.parametrize("system_enabled", [True, False])
    def test_try_run(self, mock_client, model, system_enabled):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.add_generic_input("generic-input")
        if system_enabled:
            prompt_stack.add_system_input("system-input")
        prompt_stack.add_user_input("user-input")
        prompt_stack.add_assistant_input("assistant-input")
        driver = AnthropicPromptDriver(model=model, api_key="api-key")
        expected_messages = [
            {"role": "user", "content": "generic-input"},
            {"role": "user", "content": "user-input"},
            {"role": "assistant", "content": "assistant-input"},
        ]

        # When
        text_artifact = driver.try_run(prompt_stack)

        # Then
        mock_client.return_value.beta.tools.messages.create.assert_called_once_with(
            messages=expected_messages,
            stop_sequences=["<|Response|>"],
            model=driver.model,
            max_tokens=4091,
            temperature=0.1,
            top_p=0.999,
            top_k=250,
            tool_choice={"type": "auto"},
            **{"system": "system-input"} if system_enabled else {},
        )
        assert text_artifact.value == "model-output"

    @pytest.mark.parametrize(
        "model",
        [
            ("claude-instant-1.2"),
            ("claude-2.1"),
            ("claude-2.0"),
            ("claude-3-opus"),
            ("claude-3-sonnet"),
            ("claude-3-haiku"),
        ],
    )
    def test_try_run_with_tools(self, mock_client_with_tools, model):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.tools = [MockTool()]
        prompt_stack.add_system_input("system-input")
        prompt_stack.add_user_input("user-input")
        prompt_stack.add_assistant_input("assistant-input")
        driver = AnthropicPromptDriver(model=model, api_key="api-key")
        expected_messages = [
            {"role": "user", "content": "user-input"},
            {"role": "assistant", "content": "assistant-input"},
        ]

        # When
        actions_artifact = driver.try_run(prompt_stack)

        # Then
        mock_client_with_tools.return_value.beta.tools.messages.create.assert_called_once_with(
            messages=expected_messages,
            stop_sequences=["<|Response|>"],
            model=driver.model,
            max_tokens=4091,
            temperature=0.1,
            top_p=0.999,
            top_k=250,
            tool_choice={"type": "auto"},
            tools=self.TOOLS_SCHEMA,
            system="system-input",
        )
        assert isinstance(actions_artifact, ActionsArtifact)
        assert actions_artifact.actions == [
            ActionsArtifact.Action(
                tag="tool-call-id", name="ToolName", path="ActivityName", input={"values": {"test": "test input"}}
            )
        ]
        assert actions_artifact.value == "model-output"
        assert actions_artifact.to_text() == "model-output\n" + json.dumps(
            [
                {
                    "tag": "tool-call-id",
                    "name": "ToolName",
                    "path": "ActivityName",
                    "input": {"values": {"test": "test input"}},
                }
            ],
            indent=2,
        )

    @pytest.mark.parametrize(
        "model",
        [
            ("claude-instant-1.2"),
            ("claude-2.1"),
            ("claude-2.0"),
            ("claude-3-opus"),
            ("claude-3-sonnet"),
            ("claude-3-haiku"),
        ],
    )
    @pytest.mark.parametrize("system_enabled", [True, False])
    def test_try_stream_run(self, mock_stream_client, model, system_enabled):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.add_generic_input("generic-input")
        if system_enabled:
            prompt_stack.add_system_input("system-input")
        prompt_stack.add_user_input("user-input")
        prompt_stack.add_assistant_input("assistant-input")
        expected_messages = [
            {"role": "user", "content": "generic-input"},
            {"role": "user", "content": "user-input"},
            {"role": "assistant", "content": "assistant-input"},
        ]
        driver = AnthropicPromptDriver(model=model, api_key="api-key", stream=True)

        # When
        text_artifact = next(driver.try_stream(prompt_stack))

        # Then
        mock_stream_client.return_value.beta.tools.messages.create.assert_called_once_with(
            messages=expected_messages,
            stop_sequences=["<|Response|>"],
            model=driver.model,
            max_tokens=4091,
            temperature=0.1,
            stream=True,
            top_p=0.999,
            top_k=250,
            tool_choice={"type": "auto"},
            **{"system": "system-input"} if system_enabled else {},
        )
        assert text_artifact.value == "model-output"

    @pytest.mark.parametrize(
        "model",
        [
            ("claude-instant-1.2"),
            ("claude-2.1"),
            ("claude-2.0"),
            ("claude-3-opus"),
            ("claude-3-sonnet"),
            ("claude-3-haiku"),
        ],
    )
    def test_try_stream_run_with_tools(self, mock_stream_client_with_tools, model):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.tools = [MockTool()]
        prompt_stack.add_generic_input("generic-input")
        prompt_stack.add_system_input("system-input")
        prompt_stack.add_user_input("user-input")
        prompt_stack.add_assistant_input("assistant-input")
        expected_messages = [
            {"role": "user", "content": "generic-input"},
            {"role": "user", "content": "user-input"},
            {"role": "assistant", "content": "assistant-input"},
        ]
        driver = AnthropicPromptDriver(model=model, api_key="api-key", stream=True)

        expected_chunks = [
            TextArtifact(value=""),
            TextArtifact(value="thinking"),
            ActionChunkArtifact(
                value="ToolName-ActivityName", index=0, tag="tool-call-id", name="ToolName", path="ActivityName"
            ),
            ActionChunkArtifact(value="tool-output", index=0, partial_input="tool-output"),
        ]
        # When
        chunk_stream = list(driver.try_stream(prompt_stack))

        # Then
        mock_stream_client_with_tools.return_value.beta.tools.messages.create.assert_called_once_with(
            messages=expected_messages,
            stop_sequences=["<|Response|>"],
            model=driver.model,
            max_tokens=4091,
            temperature=0.1,
            stream=True,
            top_p=0.999,
            top_k=250,
            tool_choice={"type": "auto"},
            tools=self.TOOLS_SCHEMA,
            system="system-input",
        )

        for chunk, expected_chunk in zip(chunk_stream, expected_chunks):
            if isinstance(chunk, ActionChunkArtifact):
                assert chunk.value == expected_chunk.value
                assert chunk.tag == expected_chunk.tag
                assert chunk.name == expected_chunk.name
                assert chunk.path == expected_chunk.path
                assert chunk.partial_input == expected_chunk.partial_input
                assert chunk.index == expected_chunk.index
            else:
                assert chunk.value == expected_chunk.value

    def test_try_run_throws_when_prompt_stack_is_string(self):
        # Given
        prompt_stack = "prompt-stack"
        driver = AnthropicPromptDriver(model="claude", api_key="api-key")

        # When
        with pytest.raises(Exception) as e:
            driver.try_run(prompt_stack)  # pyright: ignore

        # Then
        assert e.value.args[0] == "'str' object has no attribute 'inputs'"
