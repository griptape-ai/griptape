import pytest
from griptape.artifacts import TextArtifact
from griptape.tasks.action_subtask import ActionSubtask
from griptape.tools import TaskMemoryClient
from tests.utils import defaults


class TestTaskMemoryClient:
    @pytest.fixture
    def tool(self):
        subtask = ActionSubtask(input_memory=[defaults.text_task_memory("TestMemory")])
        tool = TaskMemoryClient(off_prompt=True)
        tool.attach_to(subtask)

        return tool

    def test_summarize(self, tool):
        tool.input_memory[0].store_artifact("foo", TextArtifact("test"))

        assert (
            tool.summarize({"values": {"memory_name": tool.input_memory[0].name, "artifact_namespace": "foo"}}).value
            == "mock output"
        )

    def test_query(self, tool):
        tool.input_memory[0].store_artifact("foo", TextArtifact("test"))

        assert (
            tool.query(
                {"values": {"query": "foobar", "memory_name": tool.input_memory[0].name, "artifact_namespace": "foo"}}
            ).value
            == "mock output"
        )
