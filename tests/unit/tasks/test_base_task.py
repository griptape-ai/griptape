import pytest

from griptape.artifacts import TextArtifact
from griptape.structures import Agent
from griptape.tasks import ActionSubtask, ToolkitTask
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_task import MockTask
from tests.mocks.mock_tool.tool import MockTool
from tests.utils import defaults


class TestBaseTask:
    @pytest.fixture
    def task(self):
        agent = Agent(prompt_driver=MockPromptDriver(), embedding_driver=MockEmbeddingDriver(), tools=[MockTool()])

        agent.add_task(MockTask("foobar", max_meta_memory_entries=2))

        return agent.task

    def test_meta_memories(self, task):
        subtask = ActionSubtask()

        subtask.structure = task.structure

        assert len(task.meta_memories) == 0

        task.structure.task_memory.process_output(subtask, TextArtifact("foo"))
        task.structure.task_memory.process_output(subtask, TextArtifact("foo"))
        task.structure.task_memory.process_output(subtask, TextArtifact("foo"))

        assert len(task.meta_memories) == 2

    def test_memory_validation(self):
        with pytest.raises(ValueError):
            MockTask(output_memory=[defaults.text_task_memory("Memory1"), defaults.text_task_memory("Memory1")])

    def test_off_prompt(self):
        assert ToolkitTask(task_memory=defaults.text_task_memory("TestMemory"), off_prompt=True).output_memory

        assert not ToolkitTask(task_memory=defaults.text_task_memory("TestMemory"), off_prompt=False).output_memory

    def test_find_output_memory(self):
        m1 = defaults.text_task_memory("Memory1")
        m2 = defaults.text_task_memory("Memory2")

        tool = MockTool(name="Tool1")
        task = ToolkitTask("test", tools=[tool], output_memory=[m1, m2])

        Agent().add_task(task)

        assert task.find_output_memory("Memory1") == m1
        assert task.find_output_memory("Memory2") == m2

    def test_memory(self):
        tool1 = MockTool(name="Tool1")

        tool2 = MockTool(name="Tool2")

        task = ToolkitTask(
            output_memory=[defaults.text_task_memory("Memory1"), defaults.text_task_memory("Memory2")],
            tools=[tool1, tool2],
        )

        Agent().add_task(task)

        assert len(task.output_memory) == 2
        assert task.output_memory[0].name == "Memory1"
        assert task.output_memory[1].name == "Memory2"

    def test_meta_memory(self):
        memory = defaults.text_task_memory("TestMemory")
        subtask = ActionSubtask()
        agent = Agent(task_memory=memory)

        subtask.structure = agent

        memory.process_output(subtask, TextArtifact("foo"))

    def test_find_input_memory(self):
        assert MockTask().find_input_memory("foo") is None
        assert MockTask(input_memory=[defaults.text_task_memory("foo")]).find_input_memory("foo") is not None
