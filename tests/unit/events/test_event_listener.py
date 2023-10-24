from unittest.mock import Mock
import pytest
from griptape.structures import Pipeline
from griptape.tasks import ToolkitTask, ActionSubtask
from griptape.events import (
    StartTaskEvent,
    FinishTaskEvent,
    StartSubtaskEvent,
    FinishSubtaskEvent,
    StartPromptEvent,
    FinishPromptEvent,
    StartStructureRunEvent,
    FinishStructureRunEvent,
    CompletionChunkEvent,
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

    def test_list_listeners(self, pipeline):
        event_handler_1 = Mock()
        event_handler_2 = Mock()

        pipeline.event_listeners = [event_handler_1, event_handler_2]
        # can't mock subtask events, so must manually call
        pipeline.tasks[0].subtasks[0].before_run()
        pipeline.tasks[0].subtasks[0].after_run()
        pipeline.run()

        assert event_handler_1.call_count == 9
        assert event_handler_2.call_count == 9

    def test_dict_listeners(self, pipeline):
        start_prompt_event_handler = Mock()
        finish_prompt_event_handler = Mock()
        start_task_event_handler = Mock()
        finish_task_event_handler = Mock()
        start_subtask_event_handler = Mock()
        finish_subtask_event_handler = Mock()
        start_structure_run_event_handler = Mock()
        finish_structure_run_event_handler = Mock()
        completion_chunk_handler = Mock()

        pipeline.event_listeners = {
            StartPromptEvent: [start_prompt_event_handler],
            FinishPromptEvent: [finish_prompt_event_handler],
            StartTaskEvent: [start_task_event_handler],
            FinishTaskEvent: [finish_task_event_handler],
            StartSubtaskEvent: [start_subtask_event_handler],
            FinishSubtaskEvent: [finish_subtask_event_handler],
            StartStructureRunEvent: [start_structure_run_event_handler],
            FinishStructureRunEvent: [finish_structure_run_event_handler],
            CompletionChunkEvent: [completion_chunk_handler],
        }

        # can't mock subtask events, so must manually call
        pipeline.tasks[0].subtasks[0].before_run()
        pipeline.tasks[0].subtasks[0].after_run()
        pipeline.run()

        start_task_event_handler.assert_called_once()
        finish_task_event_handler.assert_called_once()
        start_subtask_event_handler.assert_called_once()
        finish_subtask_event_handler.assert_called_once()
        start_structure_run_event_handler.assert_called_once()
        finish_structure_run_event_handler.assert_called_once()
        completion_chunk_handler.assert_called_once()

    def test_add_event_listener_to_list(self, pipeline):
        pipeline.event_listeners = []
        mock = Mock()
        pipeline.add_event_listener(StartPromptEvent, mock)
        pipeline.add_event_listener(StartPromptEvent, mock)

        assert len(pipeline.event_listeners) == 1

    def test_add_event_listener_to_dict(self, pipeline):
        start_prompt_event_handler = Mock()
        pipeline.event_listeners = {
            StartPromptEvent: [start_prompt_event_handler]
        }
        new_start_prompt_event_handler = Mock()
        pipeline.add_event_listener(
            StartPromptEvent, new_start_prompt_event_handler
        )
        pipeline.add_event_listener(
            FinishPromptEvent, new_start_prompt_event_handler
        )

        assert len(pipeline.event_listeners[StartPromptEvent]) == 2
        assert (
            len(pipeline.event_listeners[FinishPromptEvent]) == 1
        )  # pyright: ignore
