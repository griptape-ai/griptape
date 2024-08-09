import pytest

from griptape.engines import CsvExtractionEngine
from griptape.structures import Agent
from griptape.tasks import CsvExtractionTask
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestCsvExtractionTask:
    @pytest.fixture()
    def task(self):
        return CsvExtractionTask(args={"column_names": ["test1"]})

    def test_run(self, task):
        agent = Agent()

        agent.add_task(task)

        result = task.run()

        assert len(result.value) == 1
        assert result.value[0].value == {"test1": "mock output"}

    def test_config_extraction_engine(self, task):
        Agent().add_task(task)

        assert isinstance(task.extraction_engine, CsvExtractionEngine)
        assert isinstance(task.extraction_engine.prompt_driver, MockPromptDriver)
