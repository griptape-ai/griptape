import json
import pytest
from griptape.artifacts import TextArtifact
from griptape.structures import Agent
from griptape.tasks import ToolTask, ActionSubtask
from griptape.utils import PromptStack
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_tool.tool import MockTool
from tests.utils import defaults


class TestToolTask:
    @pytest.fixture
    def agent(self):
        output_dict = {"name": "MockTool", "path": "test", "input": {"values": {"test": "foobar"}}}
        return Agent(
            prompt_driver=MockPromptDriver(mock_output=json.dumps(output_dict)), embedding_driver=MockEmbeddingDriver()
        )

    def test_run_without_memory(self, agent):
        task = ToolTask(tool=MockTool(off_prompt=False))

        agent.add_task(task)

        assert task.run().to_text() == "ack foobar"

    def test_run_with_memory(self, agent):
        task = ToolTask(tool=MockTool())

        agent.add_task(task)

        agent.meta_memory = None

        assert task.run().to_text().startswith('Output of "MockTool.test" was stored in memory')

    def test_meta_memory(self):
        memory = defaults.text_task_memory("TestMemory")
        subtask = ActionSubtask()
        agent = Agent(task_memory=memory)

        subtask.structure = agent

        memory.process_output(MockTool().test, subtask, TextArtifact("foo"))

        task = ToolTask(tool=MockTool())

        agent.add_task(task)

        system_template = task.generate_system_template(PromptStack())

        assert "You have access to additional contextual information" in system_template
