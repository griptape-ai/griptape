from griptape.engines import PromptSummaryEngine
from griptape.tasks import SummaryTask
from tests.mocks.mock_prompt_driver import MockPromptDriver
from griptape.structures import Agent


class TestSummaryTask:
    def test_run(self):
        task = SummaryTask(
            "test",
            summary_engine=PromptSummaryEngine(prompt_driver=MockPromptDriver())
        )
        agent = Agent()

        agent.add_task(task)

        assert task.run().to_text() == "mock output"

    def test_to_text(self):
        task = SummaryTask("{{ test }}", context={"test": "test value"})

        Agent().add_task(task)

        assert task.input.to_text() == "test value"
        