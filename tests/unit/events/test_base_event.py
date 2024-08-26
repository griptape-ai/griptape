import time

import pytest

from griptape.artifacts.base_artifact import BaseArtifact
from griptape.events import (
    BaseEvent,
    CompletionChunkEvent,
    FinishActionsSubtaskEvent,
    FinishPromptEvent,
    FinishStructureRunEvent,
    FinishTaskEvent,
    StartActionsSubtaskEvent,
    StartPromptEvent,
    StartStructureRunEvent,
    StartTaskEvent,
)
from tests.mocks.mock_event import MockEvent


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
            "id": "917298d4bf894b0a824a8fdb26717a0c",
            "timestamp": 123,
            "model": "foo bar",
            "meta": {"foo": "bar"},
            "prompt_stack": {
                "type": "PromptStack",
                "messages": [
                    {
                        "type": "Message",
                        "role": "user",
                        "content": [
                            {"type": "TextMessageContent", "artifact": {"type": "TextArtifact", "value": "foo"}}
                        ],
                        "usage": {"type": "Usage", "input_tokens": None, "output_tokens": None},
                    },
                    {
                        "type": "Message",
                        "role": "system",
                        "content": [
                            {"type": "TextMessageContent", "artifact": {"type": "TextArtifact", "value": "bar"}}
                        ],
                        "usage": {"type": "Usage", "input_tokens": None, "output_tokens": None},
                    },
                ],
            },
        }

        event = BaseEvent.from_dict(dict_value)

        assert isinstance(event, StartPromptEvent)
        assert event.timestamp == 123
        assert event.prompt_stack.messages[0].content[0].artifact.value == "foo"
        assert event.prompt_stack.messages[0].role == "user"
        assert event.prompt_stack.messages[1].content[0].artifact.value == "bar"
        assert event.prompt_stack.messages[1].role == "system"
        assert event.model == "foo bar"
        assert event.meta == {"foo": "bar"}

    def test_finish_prompt_event_from_dict(self):
        dict_value = {
            "type": "FinishPromptEvent",
            "meta": {"foo": "bar"},
            "timestamp": 123.0,
            "input_token_count": 10,
            "output_token_count": 12,
            "result": "foo bar",
            "model": "foo bar",
        }

        event = BaseEvent.from_dict(dict_value)

        assert isinstance(event, FinishPromptEvent)
        assert event.timestamp == 123
        assert event.input_token_count == 10
        assert event.output_token_count == 12
        assert event.result == "foo bar"
        assert event.model == "foo bar"
        assert event.meta == {"foo": "bar"}

    def test_start_task_event_from_dict(self):
        dict_value = {
            "type": "StartTaskEvent",
            "meta": {"foo": "bar"},
            "timestamp": 123.0,
            "task_id": "foo",
            "task_parent_ids": ["bar"],
            "task_child_ids": ["baz"],
            "task_input": {"type": "TextArtifact", "value": "foo"},
            "task_output": {"type": "TextArtifact", "value": "bar"},
        }

        event = BaseEvent.from_dict(dict_value)

        assert isinstance(event, StartTaskEvent)
        assert event.timestamp == 123
        assert event.task_id == "foo"
        assert event.task_parent_ids == ["bar"]
        assert event.task_child_ids == ["baz"]
        assert isinstance(event.task_input, BaseArtifact)
        assert event.task_input.value == "foo"
        assert event.task_output.value == "bar"
        assert event.meta == {"foo": "bar"}

    def test_start_subtask_event_from_dict(self):
        dict_value = {
            "type": "StartActionsSubtaskEvent",
            "meta": {"foo": "bar"},
            "timestamp": 123.0,
            "task_id": "foo",
            "task_parent_ids": ["bar"],
            "task_child_ids": ["baz"],
            "task_input": {"type": "TextArtifact", "value": "foo"},
            "task_output": {"type": "TextArtifact", "value": "bar"},
            "subtask_parent_task_id": "foo",
            "subtask_thought": "bar",
            "subtask_actions": [{"tag": "foo", "name": "qux", "path": "foopath", "input": {"value": "quux"}}],
        }

        event = BaseEvent.from_dict(dict_value)

        assert isinstance(event, StartActionsSubtaskEvent)
        assert event.timestamp == 123
        assert event.task_id == "foo"
        assert event.task_parent_ids == ["bar"]
        assert event.task_child_ids == ["baz"]
        assert isinstance(event.task_input, BaseArtifact)
        assert event.task_input.value == "foo"
        assert event.task_output.value == "bar"
        assert event.subtask_thought == "bar"
        assert event.subtask_actions is not None
        assert event.subtask_actions[0]["tag"] == "foo"
        assert event.subtask_actions[0]["name"] == "qux"
        assert event.subtask_actions[0]["path"] == "foopath"
        assert event.subtask_actions[0]["input"] is not None
        assert event.subtask_actions[0]["input"]["value"] == "quux"
        assert event.meta == {"foo": "bar"}

    def test_finish_task_event_from_dict(self):
        dict_value = {
            "type": "FinishTaskEvent",
            "meta": {"foo": "bar"},
            "timestamp": 123.0,
            "task_id": "foo",
            "task_parent_ids": ["bar"],
            "task_child_ids": ["baz"],
            "task_input": {"type": "TextArtifact", "value": "foo"},
            "task_output": {"type": "TextArtifact", "value": "bar"},
        }

        event = BaseEvent.from_dict(dict_value)

        assert isinstance(event, FinishTaskEvent)
        assert event.timestamp == 123
        assert event.task_id == "foo"
        assert event.task_parent_ids == ["bar"]
        assert event.task_child_ids == ["baz"]
        assert isinstance(event.task_input, BaseArtifact)
        assert event.task_input.value == "foo"
        assert event.task_output.value == "bar"
        assert event.meta == {"foo": "bar"}

    def test_finish_subtask_event_from_dict(self):
        dict_value = {
            "type": "FinishActionsSubtaskEvent",
            "meta": {"foo": "bar"},
            "timestamp": 123.0,
            "task_id": "foo",
            "task_parent_ids": ["bar"],
            "task_child_ids": ["baz"],
            "task_input": {"type": "TextArtifact", "value": "foo"},
            "task_output": {"type": "TextArtifact", "value": "bar"},
            "subtask_parent_task_id": "foo",
            "subtask_thought": "bar",
            "subtask_actions": [{"tag": "foo", "name": "qux", "path": "foopath", "input": {"value": "quux"}}],
        }

        event = BaseEvent.from_dict(dict_value)

        assert isinstance(event, FinishActionsSubtaskEvent)
        assert event.timestamp == 123
        assert event.task_id == "foo"
        assert event.task_parent_ids == ["bar"]
        assert event.task_child_ids == ["baz"]
        assert isinstance(event.task_input, BaseArtifact)
        assert event.task_input.value == "foo"
        assert event.task_output.value == "bar"
        assert event.subtask_thought == "bar"
        assert event.subtask_actions is not None
        assert event.subtask_actions[0]["tag"] == "foo"
        assert event.subtask_actions[0]["name"] == "qux"
        assert event.subtask_actions[0]["path"] == "foopath"
        assert event.subtask_actions[0]["input"] is not None
        assert event.subtask_actions[0]["input"]["value"] == "quux"
        assert event.meta == {"foo": "bar"}

    def test_start_structure_run_event_from_dict(self):
        dict_value = {
            "type": "StartStructureRunEvent",
            "meta": {"foo": "bar"},
            "timestamp": 123.0,
            "structure_id": "foo",
            "input_task_input": {"type": "TextArtifact", "value": "foo"},
            "input_task_output": {"type": "TextArtifact", "value": "bar"},
        }

        event = BaseEvent.from_dict(dict_value)

        assert isinstance(event, StartStructureRunEvent)
        assert event.timestamp == 123
        assert isinstance(event.input_task_input, BaseArtifact)
        assert event.input_task_input.value == "foo"
        assert event.input_task_output.value == "bar"
        assert event.meta == {"foo": "bar"}

    def test_finish_structure_run_event_from_dict(self):
        dict_value = {
            "type": "FinishStructureRunEvent",
            "meta": {"foo": "bar"},
            "timestamp": 123.0,
            "structure_id": "foo",
            "output_task_input": {"type": "TextArtifact", "value": "foo"},
            "output_task_output": {"type": "TextArtifact", "value": "bar"},
        }

        event = BaseEvent.from_dict(dict_value)

        assert isinstance(event, FinishStructureRunEvent)
        assert event.timestamp == 123
        assert isinstance(event.output_task_input, BaseArtifact)
        assert event.output_task_input.value == "foo"
        assert event.output_task_output.value == "bar"
        assert event.meta == {"foo": "bar"}

    def test_completion_chunk_event_from_dict(self):
        dict_value = {"type": "CompletionChunkEvent", "timestamp": 123.0, "token": "foo", "meta": {}}

        event = BaseEvent.from_dict(dict_value)

        assert isinstance(event, CompletionChunkEvent)
        assert event.token == "foo"
        assert event.meta == {}

    def test_unsupported_from_dict(self):
        dict_value = {"type": "foo", "value": "foobar"}
        with pytest.raises(ValueError):
            BaseEvent.from_dict(dict_value)
