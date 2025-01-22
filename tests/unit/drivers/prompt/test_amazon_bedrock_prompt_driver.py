import pytest
from schema import Schema

from griptape.artifacts import ActionArtifact, ErrorArtifact, GenericArtifact, ImageArtifact, ListArtifact, TextArtifact
from griptape.common import ActionCallDeltaMessageContent, PromptStack, TextDeltaMessageContent, ToolAction
from griptape.drivers.prompt.amazon_bedrock import AmazonBedrockPromptDriver
from tests.mocks.mock_tool.tool import MockTool


class TestAmazonBedrockPromptDriver:
    BEDROCK_TOOLS = [
        {
            "toolSpec": {
                "description": "test description: foo",
                "inputSchema": {
                    "json": {
                        "$id": "http://json-schema.org/draft-07/schema#",
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
                    }
                },
                "name": "MockTool_test",
            }
        },
        {
            "toolSpec": {
                "description": "test description",
                "inputSchema": {
                    "json": {
                        "$id": "http://json-schema.org/draft-07/schema#",
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
                    }
                },
                "name": "MockTool_test_callable_schema",
            }
        },
        {
            "toolSpec": {
                "description": "test description: foo",
                "inputSchema": {
                    "json": {
                        "$id": "http://json-schema.org/draft-07/schema#",
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
                    }
                },
                "name": "MockTool_test_error",
            }
        },
        {
            "toolSpec": {
                "description": "test description: foo",
                "inputSchema": {
                    "json": {
                        "$id": "http://json-schema.org/draft-07/schema#",
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
                    }
                },
                "name": "MockTool_test_exception",
            }
        },
        {
            "toolSpec": {
                "description": "test description",
                "inputSchema": {
                    "json": {
                        "$id": "http://json-schema.org/draft-07/schema#",
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "additionalProperties": False,
                        "properties": {},
                        "required": [],
                        "type": "object",
                    }
                },
                "name": "MockTool_test_list_output",
            }
        },
        {
            "toolSpec": {
                "description": "test description",
                "inputSchema": {
                    "json": {
                        "$id": "http://json-schema.org/draft-07/schema#",
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "additionalProperties": False,
                        "properties": {},
                        "required": [],
                        "type": "object",
                    }
                },
                "name": "MockTool_test_no_schema",
            }
        },
        {
            "toolSpec": {
                "description": "test description: foo",
                "inputSchema": {
                    "json": {
                        "$id": "http://json-schema.org/draft-07/schema#",
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
                    }
                },
                "name": "MockTool_test_str_output",
            }
        },
        {
            "toolSpec": {
                "description": "test description",
                "inputSchema": {
                    "json": {
                        "$id": "http://json-schema.org/draft-07/schema#",
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
                    }
                },
                "name": "MockTool_test_without_default_memory",
            }
        },
    ]

    @pytest.fixture()
    def mock_converse(self, mocker):
        mock_converse = mocker.patch("boto3.Session").return_value.client.return_value.converse

        mock_converse.return_value = {
            "output": {
                "message": {
                    "content": [
                        {"text": "model-output"},
                        {"toolUse": {"name": "MockTool_test", "toolUseId": "mock-id", "input": {"foo": "bar"}}},
                    ]
                }
            },
            "usage": {"inputTokens": 5, "outputTokens": 10},
        }

        return mock_converse

    @pytest.fixture()
    def mock_converse_stream(self, mocker):
        mock_converse_stream = mocker.patch("boto3.Session").return_value.client.return_value.converse_stream

        mock_converse_stream.return_value = {
            "stream": [
                {"contentBlockStart": {"contentBlockIndex": 0, "start": {"text": "model-output"}}},
                {"contentBlockDelta": {"contentBlockIndex": 0, "delta": {"text": "model-output"}}},
                {
                    "contentBlockStart": {
                        "contentBlockIndex": 1,
                        "start": {"toolUse": {"name": "MockTool_test", "toolUseId": "mock-id"}},
                    }
                },
                {"contentBlockDelta": {"contentBlockIndex": 1, "delta": {"toolUse": {"input": '{"foo": "bar"}'}}}},
                {"metadata": {"usage": {"inputTokens": 5, "outputTokens": 10}}},
            ]
        }

        return mock_converse_stream

    @pytest.fixture(params=[True, False])
    def prompt_stack(self, request):
        prompt_stack = PromptStack()
        prompt_stack.tools = [MockTool()]
        prompt_stack.output_schema = Schema({"foo": str})
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
        prompt_stack.add_user_message(GenericArtifact("video-file"))

        return prompt_stack

    @pytest.fixture()
    def messages(self):
        return [
            {"role": "user", "content": [{"text": "user-input"}]},
            {
                "role": "user",
                "content": [{"text": "user-input"}, {"image": {"format": "png", "source": {"bytes": b"image-data"}}}],
            },
            {"role": "assistant", "content": [{"text": "assistant-input"}]},
            {
                "content": [
                    {"text": "thought"},
                    {"toolUse": {"input": {"foo": "bar"}, "name": "MockTool_test", "toolUseId": "MockTool_test"}},
                ],
                "role": "assistant",
            },
            {
                "content": [
                    {
                        "toolResult": {
                            "content": [{"text": "tool-output"}],
                            "status": "success",
                            "toolUseId": "MockTool_test",
                        }
                    },
                    {"text": "keep-going"},
                ],
                "role": "user",
            },
            {
                "content": [
                    {
                        "toolResult": {
                            "content": [
                                {"text": "tool-output"},
                                {"image": {"format": "png", "source": {"bytes": b"image-data"}}},
                            ],
                            "status": "success",
                            "toolUseId": "MockTool_test",
                        }
                    },
                    {"text": "keep-going"},
                ],
                "role": "user",
            },
            {
                "content": [
                    {"toolResult": {"content": [{"text": "error"}], "status": "error", "toolUseId": "MockTool_test"}},
                    {"text": "keep-going"},
                ],
                "role": "user",
            },
            {"content": ["video-file"], "role": "user"},
        ]

    @pytest.mark.parametrize("use_native_tools", [True, False])
    @pytest.mark.parametrize("structured_output_strategy", ["tool", "rule", "foo"])
    def test_try_run(self, mock_converse, prompt_stack, messages, use_native_tools, structured_output_strategy):
        # Given
        driver = AmazonBedrockPromptDriver(
            model="ai21.j2",
            use_native_tools=use_native_tools,
            structured_output_strategy=structured_output_strategy,
            extra_params={"foo": "bar"},
        )

        # When
        message = driver.try_run(prompt_stack)

        # Then
        mock_converse.assert_called_once_with(
            modelId=driver.model,
            messages=messages,
            inferenceConfig={
                "temperature": driver.temperature,
                **({"maxTokens": driver.max_tokens} if driver.max_tokens else {}),
            },
            additionalModelRequestFields={},
            **({"system": [{"text": "system-input"}]} if prompt_stack.system_messages else {"system": []}),
            **(
                {
                    "toolConfig": {
                        "tools": self.BEDROCK_TOOLS,
                        "toolChoice": {"any": {}}
                        if driver.structured_output_strategy == "tool"
                        else driver.tool_choice,
                    }
                }
                if use_native_tools
                else {}
            ),
            foo="bar",
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
    @pytest.mark.parametrize("structured_output_strategy", ["tool", "rule", "foo"])
    def test_try_stream_run(
        self, mock_converse_stream, prompt_stack, messages, use_native_tools, structured_output_strategy
    ):
        # Given
        driver = AmazonBedrockPromptDriver(
            model="ai21.j2",
            stream=True,
            use_native_tools=use_native_tools,
            structured_output_strategy=structured_output_strategy,
            extra_params={"foo": "bar"},
        )

        # When
        stream = driver.try_stream(prompt_stack)
        event = next(stream)

        # Then
        mock_converse_stream.assert_called_once_with(
            modelId=driver.model,
            messages=messages,
            inferenceConfig={
                "temperature": driver.temperature,
                **({"maxTokens": driver.max_tokens} if driver.max_tokens else {}),
            },
            additionalModelRequestFields={},
            **({"system": [{"text": "system-input"}]} if prompt_stack.system_messages else {"system": []}),
            **(
                {
                    "toolConfig": {
                        "tools": self.BEDROCK_TOOLS,
                        "toolChoice": {"any": {}}
                        if driver.structured_output_strategy == "tool"
                        else driver.tool_choice,
                    }
                }
                if use_native_tools
                else {}
            ),
            foo="bar",
        )

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
        assert event.usage.input_tokens == 5
        assert event.usage.output_tokens == 10

    def test_verify_structured_output_strategy(self):
        assert AmazonBedrockPromptDriver(model="foo", structured_output_strategy="tool")

        with pytest.raises(
            ValueError, match="AmazonBedrockPromptDriver does not support `native` structured output strategy."
        ):
            AmazonBedrockPromptDriver(model="foo", structured_output_strategy="native")
