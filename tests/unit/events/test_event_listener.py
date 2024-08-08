from unittest.mock import Mock

import pytest

from griptape.events import (
    CompletionChunkEvent,
    EventListener,
    FinishActionsSubtaskEvent,
    FinishPromptEvent,
    FinishStructureRunEvent,
    FinishTaskEvent,
    StartActionsSubtaskEvent,
    StartPromptEvent,
    StartStructureRunEvent,
    StartTaskEvent,
    event_bus,
)
from griptape.events.base_event import BaseEvent
from griptape.structures import Pipeline
from griptape.tasks import ActionsSubtask, ToolkitTask
from tests.mocks.mock_event import MockEvent
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_tool.tool import MockTool


class TestEventListener:
    @pytest.fixture()
    def pipeline(self):
        task = ToolkitTask("test", tools=[MockTool(name="Tool1")])

        pipeline = Pipeline(prompt_driver=MockPromptDriver(stream=True))
        pipeline.add_task(task)

        task.add_subtask(ActionsSubtask("foo"))
        return pipeline

    def test_untyped_listeners(self, pipeline):
        event_handler_1 = Mock()
        event_handler_2 = Mock()

        event_bus.add_event_listeners([EventListener(handler=event_handler_1), EventListener(handler=event_handler_2)])

        # can't mock subtask events, so must manually call
        pipeline.tasks[0].subtasks[0].before_run()
        pipeline.tasks[0].subtasks[0].after_run()
        pipeline.run()

        assert event_handler_1.call_count == 9
        assert event_handler_2.call_count == 9

    def test_typed_listeners(self, pipeline):
        start_prompt_event_handler = Mock()
        finish_prompt_event_handler = Mock()
        start_task_event_handler = Mock()
        finish_task_event_handler = Mock()
        start_subtask_event_handler = Mock()
        finish_subtask_event_handler = Mock()
        start_structure_run_event_handler = Mock()
        finish_structure_run_event_handler = Mock()
        completion_chunk_handler = Mock()

        event_bus.add_event_listeners(
            [
                EventListener(start_prompt_event_handler, event_types=[StartPromptEvent]),
                EventListener(finish_prompt_event_handler, event_types=[FinishPromptEvent]),
                EventListener(start_task_event_handler, event_types=[StartTaskEvent]),
                EventListener(finish_task_event_handler, event_types=[FinishTaskEvent]),
                EventListener(start_subtask_event_handler, event_types=[StartActionsSubtaskEvent]),
                EventListener(finish_subtask_event_handler, event_types=[FinishActionsSubtaskEvent]),
                EventListener(start_structure_run_event_handler, event_types=[StartStructureRunEvent]),
                EventListener(finish_structure_run_event_handler, event_types=[FinishStructureRunEvent]),
                EventListener(completion_chunk_handler, event_types=[CompletionChunkEvent]),
            ]
        )

        # can't mock subtask events, so must manually call
        pipeline.tasks[0].subtasks[0].before_run()
        pipeline.tasks[0].subtasks[0].after_run()
        pipeline.run()

        start_prompt_event_handler.assert_called_once()
        finish_prompt_event_handler.assert_called_once()
        start_task_event_handler.assert_called_once()
        finish_task_event_handler.assert_called_once()
        start_subtask_event_handler.assert_called_once()
        finish_subtask_event_handler.assert_called_once()
        start_structure_run_event_handler.assert_called_once()
        finish_structure_run_event_handler.assert_called_once()
        completion_chunk_handler.assert_called_once()

    def test_add_remove_event_listener(self, pipeline):
        event_bus.clear_event_listeners()
        mock1 = Mock()
        mock2 = Mock()
        # duplicate event listeners will only get added once
        event_listener_1 = event_bus.add_event_listener(EventListener(mock1, event_types=[StartPromptEvent]))
        event_bus.add_event_listener(EventListener(mock1, event_types=[StartPromptEvent]))

        event_listener_3 = event_bus.add_event_listener(EventListener(mock1, event_types=[FinishPromptEvent]))
        event_listener_4 = event_bus.add_event_listener(EventListener(mock2, event_types=[StartPromptEvent]))

        event_listener_5 = event_bus.add_event_listener(EventListener(mock2))

        assert len(event_bus.event_listeners) == 4

        event_bus.remove_event_listener(event_listener_1)
        event_bus.remove_event_listener(event_listener_3)
        event_bus.remove_event_listener(event_listener_4)
        event_bus.remove_event_listener(event_listener_5)
        assert len(event_bus.event_listeners) == 0

    def test_publish_event(self):
        mock_event_listener_driver = Mock()
        mock_event_listener_driver.try_publish_event_payload.return_value = None

        def event_handler(_: BaseEvent) -> None:
            return None

        mock_event = MockEvent()
        event_listener = EventListener(event_handler, driver=mock_event_listener_driver, event_types=[MockEvent])
        event_listener.publish_event(mock_event)

        mock_event_listener_driver.publish_event.assert_called_once_with(mock_event, flush=False)

    def test_publish_transformed_event(self):
        mock_event_listener_driver = Mock()
        mock_event_listener_driver.publish_event.return_value = None

        def event_handler(event: BaseEvent):
            return {"event": event.to_dict()}

        mock_event = MockEvent()
        event_listener = EventListener(event_handler, driver=mock_event_listener_driver, event_types=[MockEvent])
        event_listener.publish_event(mock_event)

        mock_event_listener_driver.publish_event.assert_called_once_with({"event": mock_event.to_dict()}, flush=False)
