import os
import pytest
from griptape.artifacts.text_artifact import TextArtifact
from griptape.tasks import StructureRunTask
from griptape.structures import Agent
from tests.mocks.mock_prompt_driver import MockPromptDriver
from griptape.drivers import LocalStructureRunDriver
from griptape.structures import Pipeline


class TestLocalStructureRunDriver:
    def test_run(self):
        pipeline = Pipeline()
        driver = LocalStructureRunDriver(structure_factory_fn=lambda: Agent(prompt_driver=MockPromptDriver()))

        task = StructureRunTask(driver=driver)

        pipeline.add_task(task)

        assert task.run().to_text() == "mock output"

    def test_run_with_env(self):
        pipeline = Pipeline()

        agent = Agent(prompt_driver=MockPromptDriver(mock_output=lambda: os.environ["key"]))
        driver = LocalStructureRunDriver(structure_factory_fn=lambda: agent, env={"key": "value"})
        task = StructureRunTask(driver=driver)

        pipeline.add_task(task)

        assert task.run().to_text() == "value"
