import logging
from unittest.mock import Mock, call, patch

import pytest

from griptape.configs import Defaults
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
            input_fn=input,
            output_fn=logging.info,
            logger_level=logging.INFO,
        )
        assert chat.structure == agent
        assert chat.exiting_text == "foo..."
        assert chat.processing_text == "bar..."
        assert chat.intro_text == "hello..."
        assert chat.prompt_prefix == "Question: "
        assert chat.response_prefix == "Answer: "
        assert callable(chat.input_fn)
        assert callable(chat.output_fn)
        assert chat.logger_level == logging.INFO

    @patch("builtins.input", side_effect=["exit"])
    def test_start_chat_logger_level(self, mock_input):
        agent = Agent(conversation_memory=ConversationMemory())

        chat = Chat(agent)

        logger = logging.getLogger(Defaults.logging_config.logger_name)
        logger.setLevel(logging.DEBUG)

        assert logger.getEffectiveLevel() == logging.DEBUG

        chat.start()

        assert logger.getEffectiveLevel() == logging.DEBUG
        assert mock_input.call_count == 1

    def test_chat_prompt(self):
        assert Chat.ChatPrompt.prompt_suffix == ""

    @pytest.mark.parametrize("stream", [True, False])
    @patch("builtins.input", side_effect=["foo", "exit"])
    def test_start(self, mock_input, stream):
        mock_output_fn = Mock()
        agent = Agent(conversation_memory=ConversationMemory(), stream=stream)

        chat = Chat(agent, intro_text="foo", output_fn=mock_output_fn)

        chat.start()

        mock_input.assert_has_calls([call(), call()])
        if stream:
            mock_output_fn.assert_has_calls(
                [
                    call("foo"),
                    call("Thinking..."),
                    call("Assistant: mock output", stream=True),
                    call("\n", stream=True),
                    call("Exiting..."),
                ]
            )
        else:
            mock_output_fn.assert_has_calls(
                [
                    call("foo"),
                    call("Thinking..."),
                    call("Assistant: mock output"),
                    call("Exiting..."),
                ]
            )
