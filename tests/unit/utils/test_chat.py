from griptape.memory.structure import ConversationMemory
from griptape.structures import Agent
from griptape.utils import Chat
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestConversation:
    def test_init(self):
        import logging

        agent = Agent(
            prompt_driver=MockPromptDriver(), memory=ConversationMemory()
        )

        chat = Chat(
            agent,
            exit_keywords=["exit", "bye"],
            exiting_text="foo...",
            processing_text="bar...",
            intro_text="hello...",
            prompt_prefix="Question: ",
            response_prefix="Answer: ",
            output_fn=logging.info,
        )
        assert chat.structure == agent
        assert chat.exiting_text == "foo..."
        assert chat.processing_text == "bar..."
        assert chat.intro_text == "hello..."
        assert chat.prompt_prefix == "Question: "
        assert chat.response_prefix == "Answer: "
        assert callable(chat.output_fn)
