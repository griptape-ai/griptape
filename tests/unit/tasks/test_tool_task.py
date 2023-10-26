import json
import pytest
from griptape.structures import Agent
from griptape.tasks import ToolTask
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_tool.tool import MockTool


class TestToolTask:
    @pytest.fixture
    def agent(self):
        output_dict = {
            "type": "tool",
            "name": "MockTool",
            "activity": "test",
            "input": {"values": {"test": "foobar"}},
        }
        return Agent(
            prompt_driver=MockPromptDriver(mock_output=json.dumps(output_dict))
        )

    def test_run(self, agent):
        task = ToolTask(tool=MockTool())

        agent.add_task(task)

        assert task.run().to_text() == "ack foobar"

    def test_action_types(self):
        assert ToolTask(tool=MockTool()).action_types == ["tool"]
