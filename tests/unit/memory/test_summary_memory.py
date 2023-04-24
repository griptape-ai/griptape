from griptape.core.summarizers import PromptDriverSummarizer
from griptape.memory import SummaryMemory
from tests.mocks.mock_driver import MockDriver
from griptape.tasks import PromptTask
from griptape.structures import Pipeline


class TestSummaryMemory:
    def test_unsummarized_subtasks(self):
        memory = SummaryMemory(offset=1, summarizer=PromptDriverSummarizer(driver=MockDriver()))

        pipeline = Pipeline(memory=memory, prompt_driver=MockDriver())

        pipeline.add_tasks(
            PromptTask("test")
        )

        pipeline.run()
        pipeline.run()
        pipeline.run()
        pipeline.run()

        assert len(memory.unsummarized_runs()) == 1

    def test_after_run(self):
        memory = SummaryMemory(offset=1, summarizer=PromptDriverSummarizer(driver=MockDriver()))

        pipeline = Pipeline(memory=memory, prompt_driver=MockDriver())

        pipeline.add_tasks(
            PromptTask("test")
        )

        pipeline.run()
        pipeline.run()
        pipeline.run()
        pipeline.run()

        assert memory.summary is not None
        assert memory.summary_index == 3
