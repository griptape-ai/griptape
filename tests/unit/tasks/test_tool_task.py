import json
import pytest
from griptape.artifacts import TextArtifact
from griptape.structures import Agent
from griptape.tasks import ToolTask, ActionsSubtask
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_tool.tool import MockTool
from tests.utils import defaults


class TestToolTask:
    @pytest.fixture
    def agent(self):
        output_dict = {"tag": "foo", "name": "MockTool", "path": "test", "input": {"values": {"test": "foobar"}}}

        return Agent(
            prompt_driver=MockPromptDriver(mock_output=f"```python foo bar\n{json.dumps(output_dict)}"),
            embedding_driver=MockEmbeddingDriver(),
        )

    def test_run_without_memory(self, agent):
        task = ToolTask(tool=MockTool(off_prompt=False))

        agent.add_task(task)

        assert task.run().to_text() == "MockTool output: ack foobar"

    def test_run_with_memory(self, agent):
        task = ToolTask(tool=MockTool())

        agent.add_task(task)

        assert task.run().to_text().startswith('MockTool output: Output of "MockTool.test" was stored in memory')

    def test_meta_memory(self):
        memory = defaults.text_task_memory("TestMemory")
        subtask = ActionsSubtask()
        agent = Agent(task_memory=memory)

        subtask.structure = agent

        memory.process_output(MockTool().test, subtask, TextArtifact("foo"))

        task = ToolTask(tool=MockTool(off_prompt=False))

        agent.add_task(task)

        system_template = task.generate_system_template(task)

        assert "You have access to additional contextual information" in system_template

    def test_actions_schema(self):
        tool = MockTool()
        task = ToolTask("test", tool=tool)

        Agent().add_task(task)

        assert isinstance(task.actions_schema().json_schema("Actions Schema"), dict)
