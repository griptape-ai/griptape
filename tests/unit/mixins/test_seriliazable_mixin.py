import json
import pytest
from griptape.drivers import OpenAiChatPromptDriver
from griptape.memory.structure import ConversationMemory
from griptape.memory import TaskMemory
from tests.mocks.mock_serializable import MockSerializable
from griptape.schemas import BaseSchema
from griptape.artifacts import BaseArtifact, TextArtifact


class TestSerializableMixin:
    def test_get_schema(self):
        assert isinstance(BaseArtifact.get_schema("TextArtifact"), BaseSchema)
        assert isinstance(TextArtifact.get_schema(), BaseSchema)

    def test_from_dict(self):
        assert isinstance(BaseArtifact.from_dict({"type": "TextArtifact", "value": "foobar"}), TextArtifact)
        assert isinstance(TextArtifact.from_dict({"value": "foobar"}), TextArtifact)

    def test_from_json(self):
        assert isinstance(BaseArtifact.from_json('{"type": "TextArtifact", "value": "foobar"}'), TextArtifact)
        assert isinstance(TextArtifact.from_json('{"value": "foobar"}'), TextArtifact)

    def test_str(self):
        assert str(MockSerializable()) == json.dumps(
            {"type": "MockSerializable", "foo": "bar", "bar": None, "baz": None}
        )

    def test_to_json(self):
        assert MockSerializable().to_json() == json.dumps(
            {"type": "MockSerializable", "foo": "bar", "bar": None, "baz": None}
        )

    def test_to_dict(self):
        assert MockSerializable().to_dict() == {"type": "MockSerializable", "foo": "bar", "bar": None, "baz": None}

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
