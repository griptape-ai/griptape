import pytest

from griptape.engines import CsvExtractionEngine
from griptape.structures import Agent
from griptape.tasks import ExtractionTask


class TestExtractionTask:
    @pytest.fixture()
    def task(self):
        return ExtractionTask(extraction_engine=CsvExtractionEngine(column_names=["test1"]))

    def test_run(self, task):
        agent = Agent()

        agent.add_task(task)

        result = task.run()

        assert len(result.value) == 1
        assert result.value[0].value == "test1: mock output"
