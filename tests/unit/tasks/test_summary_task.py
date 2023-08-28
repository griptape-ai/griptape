from griptape.engines import PromptSummaryEngine
from griptape.tasks import SummaryTask
from tests.mocks.mock_prompt_driver import MockPromptDriver
from griptape.structures import Agent


class TestSummarySubtask:
    def test_run(self):
        subtask = SummaryTask(
            "test",
            summary_engine=PromptSummaryEngine(prompt_driver=MockPromptDriver())
        )
        agent = Agent()

        agent.add_task(subtask)

        assert subtask.run().to_text() == "mock output"

    def test_to_text(self):
        subtask = SummaryTask("{{ test }}", context={"test": "test value"})

        Agent().add_task(subtask)

        assert subtask.input.to_text() == "test value"
        