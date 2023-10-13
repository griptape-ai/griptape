import time
from griptape.events import StartPromptEvent, FinishPromptEvent, StartTaskEvent, FinishTaskEvent, StartSubtaskEvent, FinishSubtaskEvent
from tests.mocks.mock_event import MockEvent
from griptape.events import BaseEvent


class TestBaseEvent:
    def test_timestamp(self):
        dt = time.time()

        assert MockEvent(timestamp=dt).timestamp == dt
        assert MockEvent().timestamp >= dt

    def test_to_dict(self):
        assert "timestamp" in MockEvent().to_dict()

    def test_start_prompt_event_from_dict(self):
        dict_value = {
            "type": "StartPromptEvent",
            "token_count": 10,
        }
        
        artifact = BaseEvent.from_dict(dict_value)

        assert isinstance(artifact, StartPromptEvent)
        assert artifact.token_count == 10

    def test_finish_prompt_event_from_dict(self):
        dict_value = {
            "type": "FinishPromptEvent",
            "token_count": 10,
        }
        
        artifact = BaseEvent.from_dict(dict_value)

        assert isinstance(artifact, FinishPromptEvent)
        assert artifact.token_count == 10

    def test_start_task_event_from_dict(self):
        dict_value = {
            "type": "StartTaskEvent",
            "task": {
                "type": "PromptTask",
                "output": {
                    "type": "TextArtifact",
                    "value": "foo",
                }
            },
        }
        
        artifact = BaseEvent.from_dict(dict_value)

        assert isinstance(artifact, StartTaskEvent)
        assert artifact.task.output == "foo"

    def test_start_subtask_event_from_dict(self):
        dict_value = {
            "type": "StartSubtaskEvent",
            "subtask": {
                "type": "ActionSubtask",
                "thought": "foo",
                "action_type": "bar",
                "action_name": "baz",
                "action_activity": "qux",
                "action_input": "quux",
            },
        }
        
        artifact = BaseEvent.from_dict(dict_value)

        assert isinstance(artifact, StartSubtaskEvent)
        assert artifact.subtask.thought == "foo"
        assert artifact.subtask.action_type == "bar"
        assert artifact.subtask.action_name == "baz"
        assert artifact.subtask.action_activity == "qux"
        assert artifact.subtask.action_input == "quux"

    def test_finish_subtask_event_from_dict(self):
        dict_value = {
            "type": "FinishSubtaskEvent",
            "subtask": {
                "type": "ActionSubtask",
                "thought": "foo",
                "action_type": "bar",
                "action_name": "baz",
                "action_activity": "qux",
                "action_input": "quux",
            },
        }
        
        artifact = BaseEvent.from_dict(dict_value)

        assert isinstance(artifact, FinishSubtaskEvent)
        assert artifact.subtask.thought == "foo"
        assert artifact.subtask.action_type == "bar"
        assert artifact.subtask.action_name == "baz"
        assert artifact.subtask.action_activity == "qux"
        assert artifact.subtask.action_input == "quux"

    def test_unsupported_from_dict(self):

        mock_event = MockEvent()
        try:
            BaseEvent.from_dict(mock_event)
            assert False
        except ValueError:
            assert True
