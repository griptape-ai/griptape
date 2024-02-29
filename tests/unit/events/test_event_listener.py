from unittest.mock import Mock
import pytest
from griptape.structures import Pipeline
from griptape.tasks import ToolkitTask, ActionSubtask
from griptape.events import (
    StartTaskEvent,
    FinishTaskEvent,
    StartActionSubtaskEvent,
    FinishActionSubtaskEvent,
    StartPromptEvent,
    FinishPromptEvent,
    StartStructureRunEvent,
    FinishStructureRunEvent,
    CompletionChunkEvent,
    EventListener,
)
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_tool.tool import MockTool


class TestEventListener:
    @pytest.fixture
    def pipeline(self):
        task = ToolkitTask("test", tools=[MockTool(name="Tool1")])

        pipeline = Pipeline(prompt_driver=MockPromptDriver(stream=True))
        pipeline.add_task(task)

        task.add_subtask(ActionSubtask("foo"))
        return pipeline

    def test_untyped_listeners(self, pipeline):
        event_handler_1 = Mock()
        event_handler_2 = Mock()

        pipeline.event_listeners = [EventListener(handler=event_handler_1), EventListener(handler=event_handler_2)]
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

        pipeline.event_listeners = [
            EventListener(start_prompt_event_handler, event_types=[StartPromptEvent]),
            EventListener(finish_prompt_event_handler, event_types=[FinishPromptEvent]),
            EventListener(start_task_event_handler, event_types=[StartTaskEvent]),
            EventListener(finish_task_event_handler, event_types=[FinishTaskEvent]),
            EventListener(start_subtask_event_handler, event_types=[StartActionSubtaskEvent]),
            EventListener(finish_subtask_event_handler, event_types=[FinishActionSubtaskEvent]),
            EventListener(start_structure_run_event_handler, event_types=[StartStructureRunEvent]),
            EventListener(finish_structure_run_event_handler, event_types=[FinishStructureRunEvent]),
            EventListener(completion_chunk_handler, event_types=[CompletionChunkEvent]),
        ]

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
        pipeline.event_listeners = []
        mock1 = Mock()
        mock2 = Mock()
        # duplicate event listeners will only get added once
        event_listener_1 = pipeline.add_event_listener(EventListener(mock1, event_types=[StartPromptEvent]))
        pipeline.add_event_listener(EventListener(mock1, event_types=[StartPromptEvent]))

        event_listener_3 = pipeline.add_event_listener(EventListener(mock1, event_types=[FinishPromptEvent]))
        event_listener_4 = pipeline.add_event_listener(EventListener(mock2, event_types=[StartPromptEvent]))

        event_listener_5 = pipeline.add_event_listener(EventListener(mock2))

        assert len(pipeline.event_listeners) == 4

        pipeline.remove_event_listener(event_listener_1)
        pipeline.remove_event_listener(event_listener_3)
        pipeline.remove_event_listener(event_listener_4)
        pipeline.remove_event_listener(event_listener_5)
        assert len(pipeline.event_listeners) == 0
