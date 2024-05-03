import pytest
from griptape.tasks import StructureRunTask
from griptape.structures import Agent
from tests.mocks.mock_prompt_driver import MockPromptDriver
from griptape.drivers import LocalStructureRunDriver
from griptape.structures import Pipeline


class TestLocalStructureRunDriver:
    @pytest.fixture
    def driver(self):
        agent = Agent(prompt_driver=MockPromptDriver(mock_output="agent mock output"))
        driver = LocalStructureRunDriver(structure_factory_fn=lambda: agent)

        return driver

    def test_run(self, driver):
        pipeline = Pipeline(prompt_driver=MockPromptDriver(mock_output="pipeline mock output"))

        task = StructureRunTask(driver=driver)

        pipeline.add_task(task)

        assert task.run().to_text() == "agent mock output"
