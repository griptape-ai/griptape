from tests.mocks.mock_prompt_driver import MockPromptDriver
from griptape.memory.structure import (
    ConversationMemory,
    SummaryConversationMemory,
)
from griptape.tasks import PromptTask
from griptape.structures import Pipeline
from griptape.utils import Conversation


class TestConversation:
    def test_lines(self):
        pipeline = Pipeline(
            prompt_driver=MockPromptDriver(), memory=ConversationMemory()
        )

        pipeline.add_tasks(PromptTask("question 1"))

        pipeline.run()
        pipeline.run()

        lines = Conversation(pipeline.memory).lines()

        assert lines[0] == "Q: question 1"
        assert lines[1] == "A: mock output"
        assert lines[2] == "Q: question 1"
        assert lines[3] == "A: mock output"

    def test_prompt_stack_conversation_memory(self):
        pipeline = Pipeline(
            prompt_driver=MockPromptDriver(), memory=ConversationMemory()
        )

        pipeline.add_tasks(PromptTask("question 1"))

        pipeline.run()
        pipeline.run()

        lines = Conversation(pipeline.memory).prompt_stack()

        assert lines[0] == "user: question 1"
        assert lines[1] == "assistant: mock output"

    def test_prompt_stack_summary_conversation_memory(self):
        pipeline = Pipeline(
            prompt_driver=MockPromptDriver(),
            memory=SummaryConversationMemory(
                summary="foobar", prompt_driver=MockPromptDriver()
            ),
        )

        pipeline.add_tasks(PromptTask("question 1"))

        pipeline.run()
        pipeline.run()

        lines = Conversation(pipeline.memory).prompt_stack()

        assert (
            lines[0] == "user: Summary of the conversation so far: mock output"
        )
        assert lines[1] == "user: question 1"
        assert lines[2] == "assistant: mock output"

    def test___str__(self):
        pipeline = Pipeline(
            prompt_driver=MockPromptDriver(), memory=ConversationMemory()
        )

        pipeline.add_tasks(PromptTask("question 1"))

        pipeline.run()

        string = str(Conversation(pipeline.memory))

        assert string == "Q: question 1\nA: mock output"
