from griptape.drivers import LocalStructureRunDriver
from griptape.structures import Agent, Pipeline
from griptape.tasks import StructureRunTask
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestStructureRunTask:
    def test_run_single_input(self, mock_config):
        mock_config.drivers_config.prompt_driver = MockPromptDriver(mock_output="agent mock output")
        agent = Agent()
        mock_config.drivers_config.prompt_driver = MockPromptDriver(mock_output="pipeline mock output")
        pipeline = Pipeline()
        driver = LocalStructureRunDriver(create_structure=lambda: agent)

        task = StructureRunTask(driver=driver)

        pipeline.add_task(task)

        assert task.run().to_text() == "agent mock output"

    def test_run_multiple_inputs(self, mock_config):
        mock_config.drivers_config.prompt_driver = MockPromptDriver(mock_output="agent mock output")
        agent = Agent()
        mock_config.drivers_config.prompt_driver = MockPromptDriver(mock_output="pipeline mock output")
        pipeline = Pipeline()
        driver = LocalStructureRunDriver(create_structure=lambda: agent)

        task = StructureRunTask(input=["foo", "bar", "baz"], driver=driver)

        pipeline.add_task(task)

        assert task.run().to_text() == "agent mock output"
