import os
from unittest.mock import Mock

from griptape.drivers import LocalStructureRunDriver
from griptape.events import EventBus, EventListener
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

        mock_config.drivers_config.prompt_driver = MockPromptDriver(mock_output=lambda _: os.environ["KEY"])
        agent = Agent()
        driver = LocalStructureRunDriver(structure_factory_fn=lambda: agent, env={"KEY": "value"})
        task = StructureRunTask(driver=driver)

        pipeline.add_task(task)

        assert task.run().to_text() == "value"

    def test_run_with_event_listeners(self):
        event_listeners = [EventListener(), EventListener()]
        EventBus.add_event_listeners(event_listeners)
        mock_handler = Mock()
        driver = LocalStructureRunDriver(
            structure_factory_fn=lambda: Agent(), event_listeners=[EventListener(handler=mock_handler)]
        )

        driver.run()

        assert EventBus.event_listeners == event_listeners
        mock_handler.assert_called()
