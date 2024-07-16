import pytest

from griptape.memory.meta import ActionSubtaskMetaEntry, MetaMemory


class TestMetaMemory:
    @pytest.fixture()
    def memory(self):
        return MetaMemory()

    def test_add_entry(self, memory):
        assert len(memory.entries) == 0

        memory.add_entry(ActionSubtaskMetaEntry(thought="foo", actions="[]", answer="baz"))

        assert len(memory.entries) == 1
