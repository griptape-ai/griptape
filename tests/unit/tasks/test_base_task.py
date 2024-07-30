from unittest.mock import Mock

import pytest

from griptape.artifacts import TextArtifact
from griptape.events.event_listener import EventListener
from griptape.structures import Agent, Workflow
from griptape.tasks import ActionsSubtask
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_task import MockTask
from tests.mocks.mock_tool.tool import MockTool


class TestBaseTask:
    @pytest.fixture()
    def task(self):
        agent = Agent(
            prompt_driver=MockPromptDriver(),
            embedding_driver=MockEmbeddingDriver(),
            tools=[MockTool()],
            event_listeners=[EventListener(handler=Mock())],
        )

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

    def test_parent_outputs(self, task):
        parent_1 = MockTask("foobar1", id="foobar1")
        parent_2 = MockTask("foobar2", id="foobar2")
        parent_3 = MockTask("foobar3", id="foobar3")
        child = MockTask("foobar", id="foobar")

        child.add_parent(parent_1)
        child.add_parent(parent_2)
        child.add_parent(parent_3)

        workflow = Workflow(tasks=[parent_1, parent_2, parent_3, child])
        workflow.run()

        parent_3.output = None
        assert child.parent_outputs == {
            parent_1.id: parent_1.output.to_text(),
            parent_2.id: parent_2.output.to_text(),
            parent_3.id: "",
        }

    def test_parents_output(self, task):
        parent_1 = MockTask("foobar1", id="foobar1")
        parent_2 = MockTask("foobar2", id="foobar2")
        parent_3 = MockTask("foobar3", id="foobar3")
        child = MockTask("foobar", id="foobar")

        child.add_parent(parent_1)
        child.add_parent(parent_2)
        child.add_parent(parent_3)

        workflow = Workflow(tasks=[parent_1, parent_2, parent_3, child])
        workflow.run()

        parent_2.output = None

        assert child.parents_output_text == "foobar1\nfoobar3"

    def test_execute_publish_events(self, task):
        task.execute()

        assert task.structure.event_listeners[0].handler.call_count == 2
