import pytest

from griptape.engines import CsvExtractionEngine
from griptape.structures import Agent
from griptape.tasks import ExtractionTask
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestExtractionTask:
    @pytest.fixture()
    def task(self):
        return ExtractionTask(
            extraction_engine=CsvExtractionEngine(
                column_names=["test1"], prompt_driver=MockPromptDriver(mock_output="header\nmock output")
            )
        )

    def test_run(self, task):
        agent = Agent()

        agent.add_task(task)

        result = task.run()

        assert len(result.value) == 2
        assert result.value[0].value == "test1"
        assert result.value[1].value == "mock output"
