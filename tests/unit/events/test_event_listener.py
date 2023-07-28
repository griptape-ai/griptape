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
)
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_tool.tool import MockTool


class TestEventListener:
    @pytest.fixture
    def pipeline(self):
        task = ToolkitTask("test", tools=[MockTool(name="Tool1")])

        pipeline = Pipeline(prompt_driver=MockPromptDriver())
        pipeline.add_task(task)

        task.add_subtask(ActionSubtask('foo'))
        return pipeline

    def test_list_listeners(self, pipeline):
        event_handler_1 = Mock()
        event_handler_2 = Mock()

        pipeline.event_listeners = [
            event_handler_1,
            event_handler_2,
        ]
        # can't mock subtask events, so must manually call 
        pipeline.tasks[0].subtasks[0].before_run()
        pipeline.tasks[0].subtasks[0].after_run()
        pipeline.run()

        assert event_handler_1.call_count == 6
        assert event_handler_2.call_count == 6

    def test_dict_listeners(self, pipeline):
        start_task_event_handler = Mock()
        finish_task_event_handler = Mock()
        start_subtask_event_handler = Mock()
        finish_subtask_event_handler = Mock()
        start_prompt_event_handler = Mock()
        finish_prompt_event_handler = Mock()

        pipeline.event_listeners = {
            StartTaskEvent: [start_task_event_handler],
            FinishTaskEvent: [finish_task_event_handler],
            StartSubtaskEvent: [start_subtask_event_handler],
            FinishSubtaskEvent: [finish_subtask_event_handler],
            StartPromptEvent: [start_prompt_event_handler],
            FinishPromptEvent: [finish_prompt_event_handler],
        }

        # can't mock subtask events, so must manually call 
        pipeline.tasks[0].subtasks[0].before_run()
        pipeline.tasks[0].subtasks[0].after_run()
        pipeline.run()

        start_task_event_handler.assert_called_once()
        finish_task_event_handler.assert_called_once()
        start_subtask_event_handler.assert_called_once()
        finish_subtask_event_handler.assert_called_once()
        start_prompt_event_handler.assert_called_once()
        finish_prompt_event_handler.assert_called_once()
