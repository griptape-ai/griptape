from griptape.engines import PromptSummaryEngine
from griptape.tasks import TextSummaryTask
from tests.mocks.mock_prompt_driver import MockPromptDriver
from griptape.structures import Agent

class TestTextSummaryTask:
    def test_run(self):
        task = TextSummaryTask(
            "test",
            summary_engine=PromptSummaryEngine(prompt_driver=MockPromptDriver()),
            length=3,
            target_audience="executive summary",
            format="json"
        )
        agent = Agent()
        agent.add_task(task)
        assert task.run().to_text() == "mock output"
        
    def test_context_propagation(self):
        task = TextSummaryTask(
            "{{ test }}",
            context={"test": "test value"},
            length=2,
            target_audience="child",
            format="yaml"
        )
        Agent().add_task(task)
        expected_result = 'The text is a simple statement of "test value".'
        assert task.run().to_text() == expected_result
