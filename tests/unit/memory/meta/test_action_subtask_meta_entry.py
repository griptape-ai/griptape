import pytest

from griptape.memory.meta import ActionSubtaskMetaEntry


class TestActionSubtaskMetaEntry:
    @pytest.fixture()
    def entry(self):
        return ActionSubtaskMetaEntry(thought="foo", actions="[]", answer="baz")

    def test_to_dict(self, entry):
        assert entry.to_dict() == {"thought": "foo", "actions": "[]", "answer": "baz"}
