import pytest

from griptape.artifacts import TextArtifact
from griptape.structures import Agent
from griptape.tasks import ActionsSubtask
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_task import MockTask
from tests.mocks.mock_tool.tool import MockTool


class TestBaseTask:
    @pytest.fixture
    def task(self):
        agent = Agent(prompt_driver=MockPromptDriver(), embedding_driver=MockEmbeddingDriver(), tools=[MockTool()])

        agent.add_task(MockTask("foobar", max_meta_memory_entries=2))

        return agent.task

    def test_meta_memories(self, task):
        subtask = ActionsSubtask()

        subtask.structure = task.structure

        assert len(task.meta_memories) == 0

        task.structure.task_memory.process_output(MockTool().test, subtask, TextArtifact("foo"))
        task.structure.task_memory.process_output(MockTool().test, subtask, TextArtifact("foo"))
        task.structure.task_memory.process_output(MockTool().test, subtask, TextArtifact("foo"))

        assert len(task.meta_memories) == 2
