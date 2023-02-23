from galaxybrain.prompts import Prompt
from galaxybrain.summarizers import CompletionDriverSummarizer
from galaxybrain.workflows import Workflow, CompletionStep
from galaxybrain.workflows.memory import SummaryMemory
from tests.mocks.mock_driver import MockDriver


class TestSummaryMemory:
    def test_unsummarized_steps(self):
        memory = SummaryMemory(offset=1, summarizer=CompletionDriverSummarizer(driver=MockDriver()))

        workflow = Workflow(memory=memory, completion_driver=MockDriver())

        workflow.add_steps(
            CompletionStep(input=Prompt("test")),
            CompletionStep(input=Prompt("test")),
            CompletionStep(input=Prompt("test")),
            CompletionStep(input=Prompt("test"))
        )

        workflow.start()

        assert len(memory.unsummarized_steps()) == 1

    def test_after_run(self):
        memory = SummaryMemory(offset=1, summarizer=CompletionDriverSummarizer(driver=MockDriver()))

        workflow = Workflow(memory=memory, completion_driver=MockDriver())

        workflow.add_steps(
            CompletionStep(input=Prompt("test")),
            CompletionStep(input=Prompt("test")),
            CompletionStep(input=Prompt("test")),
            CompletionStep(input=Prompt("test"))
        )

        workflow.start()

        assert memory.summary is not None
        assert memory.summary_index == 3
