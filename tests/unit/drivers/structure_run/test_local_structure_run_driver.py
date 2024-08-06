import os

from griptape.drivers import LocalStructureRunDriver
from griptape.structures import Agent, Pipeline
from griptape.tasks import StructureRunTask
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestLocalStructureRunDriver:
    def test_run(self):
        pipeline = Pipeline()
        driver = LocalStructureRunDriver(structure_factory_fn=lambda: Agent())

        task = StructureRunTask(driver=driver)

        pipeline.add_task(task)

        assert task.run().to_text() == "mock output"

    def test_run_with_env(self, mock_config):
        pipeline = Pipeline()

        mock_config.prompt_driver = MockPromptDriver(mock_output=lambda _: os.environ["KEY"])
        agent = Agent()
        driver = LocalStructureRunDriver(structure_factory_fn=lambda: agent, env={"KEY": "value"})
        task = StructureRunTask(driver=driver)

        pipeline.add_task(task)

        assert task.run().to_text() == "value"
