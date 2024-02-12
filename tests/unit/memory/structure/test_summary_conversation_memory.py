import json

import pytest

from griptape.memory.structure import Run, SummaryConversationMemory
from griptape.structures import Pipeline
from griptape.tasks import PromptTask
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_structure_config import MockStructureConfig


class TestSummaryConversationMemory:
    def test_unsummarized_subtasks(self):
        memory = SummaryConversationMemory(offset=1, prompt_driver=MockPromptDriver())

        pipeline = Pipeline(conversation_memory=memory, prompt_driver=MockPromptDriver())

        pipeline.add_tasks(PromptTask("test"))

        pipeline.run()
        pipeline.run()
        pipeline.run()
        pipeline.run()

        assert len(memory.unsummarized_runs()) == 1

    def test_after_run(self):
        memory = SummaryConversationMemory(offset=1, prompt_driver=MockPromptDriver())

        pipeline = Pipeline(conversation_memory=memory, prompt_driver=MockPromptDriver())

        pipeline.add_tasks(PromptTask("test"))

        pipeline.run()
        pipeline.run()
        pipeline.run()
        pipeline.run()

        assert memory.summary is not None
        assert memory.summary_index == 3

    def test_to_json(self):
        memory = SummaryConversationMemory()
        memory.add_run(Run(input="foo", output="bar"))

        assert json.loads(memory.to_json())["type"] == "SummaryConversationMemory"
        assert json.loads(memory.to_json())["runs"][0]["input"] == "foo"

    def test_to_dict(self):
        memory = SummaryConversationMemory()
        memory.add_run(Run(input="foo", output="bar"))

        assert memory.to_dict()["type"] == "SummaryConversationMemory"
        assert memory.to_dict()["runs"][0]["input"] == "foo"

    def test_to_prompt_stack(self):
        memory = SummaryConversationMemory(summary="foobar")
        memory.add_run(Run(input="foo", output="bar"))

        prompt_stack = memory.to_prompt_stack()

        assert prompt_stack.inputs[0].content == "Summary of the conversation so far: foobar"
        assert prompt_stack.inputs[1].content == "foo"
        assert prompt_stack.inputs[2].content == "bar"

    def test_from_dict(self):
        memory = SummaryConversationMemory()
        memory.add_run(Run(input="foo", output="bar"))
        memory_dict = memory.to_dict()

        assert isinstance(memory.from_dict(memory_dict), SummaryConversationMemory)
        assert memory.from_dict(memory_dict).runs[0].input == "foo"
        assert memory.from_dict(memory_dict).runs[0].output == "bar"
        assert memory.from_dict(memory_dict).offset == memory.offset
        assert memory.from_dict(memory_dict).summary == memory.summary
        assert memory.from_dict(memory_dict).summary_index == memory.summary_index
        assert memory.from_dict(memory_dict).max_runs == memory.max_runs

    def test_from_json(self):
        memory = SummaryConversationMemory()
        memory.add_run(Run(input="foo", output="bar"))
        memory_dict = memory.to_dict()

        assert isinstance(memory.from_dict(memory_dict), SummaryConversationMemory)
        assert memory.from_dict(memory_dict).runs[0].input == "foo"

    def test_config_prompt_driver(self):
        memory = SummaryConversationMemory()
        pipeline = Pipeline(conversation_memory=memory, config=MockStructureConfig())

        pipeline.add_tasks(PromptTask("test"))

        assert isinstance(memory.prompt_driver, MockPromptDriver)
