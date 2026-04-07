import json

import pytest
from pydantic import create_model

from griptape.artifacts import BaseArtifact, TextArtifact
from griptape.drivers.prompt.openai import OpenAiChatPromptDriver
from griptape.memory import TaskMemory
from griptape.memory.structure import ConversationMemory
from griptape.schemas import BaseSchema
from griptape.tasks.base_task import BaseTask
from griptape.tasks.tool_task import ToolTask
from griptape.tools.base_tool import BaseTool
from tests.mocks.mock_serializable import MockSerializable
from tests.mocks.mock_tool.tool import MockTool


class TestSerializableMixin:
    def test_get_schema(self):
        assert isinstance(BaseArtifact.get_schema("TextArtifact"), BaseSchema)
        assert isinstance(TextArtifact.get_schema(), BaseSchema)

        assert isinstance(BaseTool.get_schema("MockTool", module_name="tests.mocks.mock_tool.tool"), BaseSchema)

    def test_from_dict(self):
        assert isinstance(BaseArtifact.from_dict({"type": "TextArtifact", "value": "foobar"}), TextArtifact)
        assert isinstance(TextArtifact.from_dict({"value": "foobar"}), TextArtifact)

        assert isinstance(
            BaseTask.from_dict(
                {"type": "ToolTask", "tool": {"type": "MockTool", "module_name": "tests.mocks.mock_tool.tool"}},
            ),
            ToolTask,
        )

    def test_from_json(self):
        assert isinstance(BaseArtifact.from_json('{"type": "TextArtifact", "value": "foobar"}'), TextArtifact)
        assert isinstance(TextArtifact.from_json('{"value": "foobar"}'), TextArtifact)

    def test_str(self):
        assert str(MockSerializable(buzz={"foo": MockSerializable()})) == json.dumps(
            {
                "type": "MockSerializable",
                "foo": "bar",
                "bar": None,
                "baz": None,
                "nested": None,
                "model": None,
                "buzz": {
                    "foo": {
                        "type": "MockSerializable",
                        "foo": "bar",
                        "bar": None,
                        "baz": None,
                        "nested": None,
                        "model": None,
                        "buzz": None,
                    }
                },
            }
        )

    def test_to_json(self):
        assert MockSerializable(model=MockSerializable.MockOutput(foo="bar")).to_json() == json.dumps(
            {
                "type": "MockSerializable",
                "foo": "bar",
                "bar": None,
                "baz": None,
                "nested": None,
                "model": {"foo": "bar"},
                "buzz": None,
            }
        )

    def test_to_dict(self):
        assert MockSerializable(model=MockSerializable.MockOutput(foo="bar")).to_dict() == {
            "type": "MockSerializable",
            "foo": "bar",
            "bar": None,
            "baz": None,
            "nested": None,
            "model": {"foo": "bar"},
            "buzz": None,
        }

    def test_import_class_rec(self):
        assert (
            MockSerializable._import_cls_rec("griptape.drivers.base_prompt_driver", "OpenAiChatPromptDriver")
            == OpenAiChatPromptDriver
        )
        assert (
            MockSerializable._import_cls_rec("griptape.memory.structure.base_conversation_memory", "ConversationMemory")
            == ConversationMemory
        )
        assert MockSerializable._import_cls_rec("griptape.memory.task.task_memory", "TaskMemory") == TaskMemory

        with pytest.raises(ValueError):
            MockSerializable._import_cls_rec("griptape.memory.task", "ConversationMemory")

        assert MockSerializable._import_cls_rec("tests.mocks.mock_tool.tool", "MockTool") == MockTool

    def test_nested_optional_serializable(self):
        assert MockSerializable(nested=None).to_dict().get("nested") is None

        assert MockSerializable(nested=MockSerializable.NestedMockSerializable()).to_dict()["nested"]["foo"] == "bar"

    def test_json_dumps_pydantic_model(self):
        output_schema = create_model(
            "AgentOutputSchema",
            generated_image_urls=(list[str], ...),
            conversation_output=(str, ...),
        )

        model_instance = output_schema(
            generated_image_urls=["http://example.com/image1.png"],
            conversation_output="Hello, Collin!",
        )

        json_str = json.dumps(model_instance)
        parsed = json.loads(json_str)

        assert parsed["generated_image_urls"] == ["http://example.com/image1.png"]
        assert parsed["conversation_output"] == "Hello, Collin!"
