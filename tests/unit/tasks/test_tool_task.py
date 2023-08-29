from griptape.structures import Agent
from griptape.tasks import SummaryTask, ToolTask


class TestToolSubtask:
    def test_run(self):
        task = ToolTask("test")
        agent = Agent()

        agent.add_task(task)

        assert task.run().to_text() == "mock output"

    def test_to_text(self):
        subtask = SummaryTask("{{ test }}", context={"test": "test value"})

        Agent().add_task(subtask)

        assert subtask.input.to_text() == "test value"
        