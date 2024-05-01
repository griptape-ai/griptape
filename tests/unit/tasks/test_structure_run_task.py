from griptape.tasks import StructureRunTask
from griptape.structures import Agent
from tests.mocks.mock_prompt_driver import MockPromptDriver
from griptape.structures import Pipeline


class TestStructureRunTask:
    def test_run(self):
        agent = Agent(prompt_driver=MockPromptDriver(mock_output="agent mock output"))
        pipeline = Pipeline(prompt_driver=MockPromptDriver(mock_output="pipeline mock output"))

        task = StructureRunTask(structure_to_run=agent)

        pipeline.add_task(task)

        assert task.run().to_text() == "agent mock output"
