import logging
from unittest.mock import patch

from griptape.config import config
from griptape.memory.structure import ConversationMemory
from griptape.structures import Agent
from griptape.utils import Chat


class TestConversation:
    def test_init(self):
        agent = Agent(conversation_memory=ConversationMemory())

        chat = Chat(
            agent,
            exit_keywords=["exit", "bye"],
            exiting_text="foo...",
            processing_text="bar...",
            intro_text="hello...",
            prompt_prefix="Question: ",
            response_prefix="Answer: ",
            output_fn=logging.info,
            logger_level=logging.INFO,
        )
        assert chat.structure == agent
        assert chat.exiting_text == "foo..."
        assert chat.processing_text == "bar..."
        assert chat.intro_text == "hello..."
        assert chat.prompt_prefix == "Question: "
        assert chat.response_prefix == "Answer: "
        assert callable(chat.output_fn)
        assert chat.logger_level == logging.INFO

    @patch("builtins.input", side_effect=["exit"])
    def test_chat_logger_level(self, mock_input):
        agent = Agent(conversation_memory=ConversationMemory())

        chat = Chat(agent)

        logger = logging.getLogger(config.logging.logger_name)
        logger.setLevel(logging.DEBUG)

        assert logger.getEffectiveLevel() == logging.DEBUG

        chat.start()

        assert logger.getEffectiveLevel() == logging.DEBUG
        assert mock_input.call_count == 1
