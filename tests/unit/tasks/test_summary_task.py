from griptape.tasks import SummaryTask
from griptape.structures import Agent


class TestSummarySubtask:
    def test_to_text(self):
        subtask = SummaryTask("{{ test }}", context={"test": "test value"})

        Agent().add_task(subtask)

        assert subtask.input.to_text() == "test value"
        