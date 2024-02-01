import pytest
from griptape.structures import Agent
from griptape.tasks import CsvExtractionTask
from tests.mocks.mock_structure_config import MockStructureConfig


class TestCsvExtractionTask:
    @pytest.fixture
    def task(self):
        return CsvExtractionTask(args={"column_names": ["test1"]})

    def test_run(self, task):
        agent = Agent(config=MockStructureConfig())

        agent.add_task(task)

        result = task.run()

        assert len(result.value) == 1
        assert result.value[0].value == {"test1": "mock output"}
