import pytest
from tests.mocks.mock_structure_config import MockStructureConfig
from griptape.engines import PromptSummaryEngine
from griptape.tasks import TextSummaryTask
from tests.mocks.mock_prompt_driver import MockPromptDriver
from griptape.structures import Agent


class TestTextSummaryTask:
    def test_run(self):
        task = TextSummaryTask("test", summary_engine=PromptSummaryEngine(prompt_driver=MockPromptDriver()))
        agent = Agent()

        agent.add_task(task)

        assert task.run().to_text() == "mock output"

    def test_context_propagation(self):
        task = TextSummaryTask("{{ test }}", context={"test": "test value"})

        Agent().add_task(task)

        assert task.input.to_text() == "test value"

    def test_config_summary_engine(self):
        task = TextSummaryTask("test")

        Agent(config=MockStructureConfig()).add_task(task)

        assert isinstance(task.summary_engine, PromptSummaryEngine)
        assert isinstance(task.summary_engine.prompt_driver, MockPromptDriver)

    def test_missing_summary_engine(self):
        task = TextSummaryTask("test")

        with pytest.raises(ValueError):
            task.summary_engine
