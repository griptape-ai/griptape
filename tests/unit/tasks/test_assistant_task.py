from griptape.structures import Pipeline
from griptape.tasks import AssistantTask
from tests.mocks.mock_assistant_driver import MockAssistantDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestAssistantTask:
    def test_run_single_input(self, mock_config):
        mock_config.drivers_config.prompt_driver = MockPromptDriver(mock_output="pipeline mock output")
        pipeline = Pipeline()
        driver = MockAssistantDriver()

        task = AssistantTask(driver=driver)

        pipeline.add_task(task)

        assert task.run().to_text() == "mock output"

    def test_run_multiple_inputs(self, mock_config):
        mock_config.drivers_config.prompt_driver = MockPromptDriver(mock_output="pipeline mock output")
        pipeline = Pipeline()
        driver = MockAssistantDriver()

        task = AssistantTask(input=["foo", "bar", "baz"], driver=driver)

        pipeline.add_task(task)

        assert task.run().to_text() == "mock output"
