import json

from griptape.artifacts import TextArtifact
from griptape.memory.structure import Run, SummaryConversationMemory
from griptape.structures import Pipeline
from griptape.tasks import PromptTask
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestSummaryConversationMemory:
    def test_unsummarized_subtasks(self):
        memory = SummaryConversationMemory(offset=1)

        pipeline = Pipeline(conversation_memory=memory)

        pipeline.add_tasks(PromptTask("test"))

        pipeline.run()
        pipeline.run()
        pipeline.run()
        pipeline.run()

        assert len(memory.unsummarized_runs()) == 1

    def test_after_run(self):
        memory = SummaryConversationMemory(offset=1)

        pipeline = Pipeline(conversation_memory=memory)

        pipeline.add_tasks(PromptTask("test"))

        pipeline.run()
        pipeline.run()
        pipeline.run()
        pipeline.run()

        assert memory.summary is not None
        assert memory.summary_index == 3

    def test_to_json(self):
        memory = SummaryConversationMemory()
        memory.add_run(Run(input=TextArtifact("foo"), output=TextArtifact("bar")))

        assert json.loads(memory.to_json())["type"] == "SummaryConversationMemory"
        assert json.loads(memory.to_json())["runs"][0]["input"]["value"] == "foo"

    def test_to_dict(self):
        memory = SummaryConversationMemory()
        memory.add_run(Run(input=TextArtifact("foo"), output=TextArtifact("bar")))

        assert memory.to_dict()["type"] == "SummaryConversationMemory"
        assert memory.to_dict()["runs"][0]["input"]["value"] == "foo"

    def test_to_prompt_stack(self):
        memory = SummaryConversationMemory(summary="foobar")
        memory.add_run(Run(input=TextArtifact("foo"), output=TextArtifact("bar")))

        prompt_stack = memory.to_prompt_stack()

        assert prompt_stack.messages[0].content[0].artifact.value == "Summary of the conversation so far: foobar"
        assert prompt_stack.messages[1].content[0].artifact.value == "foo"
        assert prompt_stack.messages[2].content[0].artifact.value == "bar"

    def test_from_dict(self):
        memory = SummaryConversationMemory()
        memory.add_run(Run(input=TextArtifact("foo"), output=TextArtifact("bar")))
        memory_dict = memory.to_dict()

        assert isinstance(memory.from_dict(memory_dict), SummaryConversationMemory)
        assert memory.from_dict(memory_dict).runs[0].input.value == "foo"
        assert memory.from_dict(memory_dict).runs[0].output.value == "bar"
        assert memory.from_dict(memory_dict).offset == memory.offset
        assert memory.from_dict(memory_dict).summary == memory.summary
        assert memory.from_dict(memory_dict).summary_index == memory.summary_index
        assert memory.from_dict(memory_dict).max_runs == memory.max_runs

    def test_from_json(self):
        memory = SummaryConversationMemory()
        memory.add_run(Run(input=TextArtifact("foo"), output=TextArtifact("bar")))
        memory_dict = memory.to_dict()

        assert isinstance(memory.from_dict(memory_dict), SummaryConversationMemory)
        assert memory.from_dict(memory_dict).runs[0].input.value == "foo"

    def test_config_prompt_driver(self):
        memory = SummaryConversationMemory()
        pipeline = Pipeline(conversation_memory=memory)

        pipeline.add_tasks(PromptTask("test"))

        assert isinstance(memory.prompt_driver, MockPromptDriver)

    def test_summary_init(self):
        memory = SummaryConversationMemory(summary="initial summary", summary_index=5)

        assert memory.meta["summary"] == "initial summary"
        assert memory.meta["summary_index"] == 5

    def test_summary_no_init(self):
        memory = SummaryConversationMemory(summary=None, summary_index=0)

        assert "summary" not in memory.meta
        assert "summary_index" not in memory.meta

    def test_summary_complete_run(self):
        original_memory = SummaryConversationMemory(summary="test summary", summary_index=2)
        original_memory.add_run(Run(input=TextArtifact("foo"), output=TextArtifact("bar")))
        memory_dict = original_memory.to_dict()
        assert memory_dict["meta"]["summary"] == "test summary"
        assert memory_dict["meta"]["summary_index"] == 2
        restored_memory = SummaryConversationMemory.from_dict(memory_dict)

        assert restored_memory.summary == "test summary"
        assert restored_memory.summary_index == 2
        assert restored_memory.meta["summary"] == "test summary"
        assert restored_memory.meta["summary_index"] == 2
