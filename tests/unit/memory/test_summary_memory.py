import json

from griptape.summarizers import PromptDriverSummarizer
from griptape.memory import SummaryMemory, Run
from tests.mocks.mock_prompt_driver import MockPromptDriver
from griptape.tasks import PromptTask
from griptape.structures import Pipeline


class TestSummaryMemory:
    def test_unsummarized_subtasks(self):
        memory = SummaryMemory(offset=1, summarizer=PromptDriverSummarizer(driver=MockPromptDriver()))

        pipeline = Pipeline(memory=memory, prompt_driver=MockPromptDriver())

        pipeline.add_tasks(
            PromptTask("test")
        )

        pipeline.run()
        pipeline.run()
        pipeline.run()
        pipeline.run()

        assert len(memory.unsummarized_runs()) == 1

    def test_after_run(self):
        memory = SummaryMemory(offset=1, summarizer=PromptDriverSummarizer(driver=MockPromptDriver()))

        pipeline = Pipeline(memory=memory, prompt_driver=MockPromptDriver())

        pipeline.add_tasks(
            PromptTask("test")
        )

        pipeline.run()
        pipeline.run()
        pipeline.run()
        pipeline.run()

        assert memory.summary is not None
        assert memory.summary_index == 3

    def test_to_json(self):
        memory = SummaryMemory()
        memory.add_run(Run(input="foo", output="bar"))

        assert json.loads(memory.to_json())["type"] == "SummaryMemory"
        assert json.loads(memory.to_json())["runs"][0]["input"] == "foo"

    def test_to_dict(self):
        memory = SummaryMemory()
        memory.add_run(Run(input="foo", output="bar"))

        assert memory.to_dict()["type"] == "SummaryMemory"
        assert memory.to_dict()["runs"][0]["input"] == "foo"

    def test_from_dict(self):
        memory = SummaryMemory()
        memory.add_run(Run(input="foo", output="bar"))
        memory_dict = memory.to_dict()

        assert isinstance(memory.from_dict(memory_dict), SummaryMemory)
        assert memory.from_dict(memory_dict).runs[0].input == "foo"

    def test_from_json(self):
        memory = SummaryMemory()
        memory.add_run(Run(input="foo", output="bar"))
        memory_dict = memory.to_dict()

        assert isinstance(memory.from_dict(memory_dict), SummaryMemory)
        assert memory.from_dict(memory_dict).runs[0].input == "foo"
