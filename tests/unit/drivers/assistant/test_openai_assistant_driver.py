from unittest.mock import ANY, Mock

import pytest

from griptape.artifacts.text_artifact import TextArtifact
from griptape.drivers.assistant.openai import OpenAiAssistantDriver
from griptape.events import EventBus
from griptape.events.event_listener import EventListener


class TestOpenAiAssistantDriver:
    @pytest.fixture(autouse=True)
    def mock_event_handler(self, mocker):
        event_handler = OpenAiAssistantDriver.EventHandler()
        mocker.patch.object(
            event_handler,
            "get_final_messages",
            return_value=[
                Mock(
                    content=[
                        Mock(type="TextContentBlock", text=Mock(value="foo")),
                        Mock(type="TextContentBlock", text=Mock(value=" bar")),
                    ]
                ),
                Mock(
                    content=[
                        Mock(type="TextContentBlock", text=Mock(value="foo")),
                        Mock(type="TextContentBlock", text=Mock(value=" bar")),
                    ]
                ),
            ],
        )
        mocker.patch.object(event_handler, "until_done")

        return event_handler

    @pytest.fixture(autouse=True)
    def mock_openai_client(self, mocker, mock_event_handler):
        mock_client = mocker.patch("openai.OpenAI")
        mock_client_instance = mock_client.return_value

        mock_client_instance.beta.threads.messages.create = Mock()
        mock_client_instance.beta.threads.create.return_value = Mock(id="thread_id")

        mock_chat_stream = mock_client_instance.beta.threads.runs.stream
        mock_chat_stream_enter = mock_chat_stream.return_value.__enter__

        def enter_side_effect(*args, **kwargs):
            mock_event_handler.on_text_delta(Mock(value=None), Mock())
            mock_event_handler.on_text_delta(Mock(value="delta_value"), Mock())

            mock_event_handler.on_tool_call_delta(Mock(type="unknown_event"), Mock())
            mock_event_handler.on_tool_call_delta(
                Mock(type="code_interpreter", code_interpreter=Mock(input="code_input", outputs=None)), Mock()
            )
            mock_event_handler.on_tool_call_delta(
                Mock(
                    type="code_interpreter",
                    code_interpreter=Mock(input=None, outputs=[Mock(type="logs", logs="output_logs")]),
                ),
                Mock(),
            )
            mock_event_handler.on_tool_call_delta(
                Mock(
                    type="code_interpreter",
                    code_interpreter=Mock(input=None, outputs=[Mock(type="unknown_type")]),
                ),
                Mock(),
            )

            return mock_event_handler

        mock_chat_stream_enter.return_value = mock_event_handler
        mock_chat_stream_enter.side_effect = enter_side_effect

        return mock_client

    @pytest.fixture()
    def driver(self):
        return OpenAiAssistantDriver(
            thread_id="thread_id",
            assistant_id="assistant_id",
        )

    @pytest.mark.parametrize("thread_id", ["thread_id", None])
    def test_run(self, driver, mock_openai_client, mock_event_handler, thread_id):
        mock_event_listener_handler = Mock()
        EventBus.add_event_listener(EventListener(mock_event_listener_handler))
        driver.thread_id = thread_id
        driver.event_handler = mock_event_handler
        result = driver.run(TextArtifact("foo bar"), TextArtifact("fizz buzz"))

        mock_openai_client.return_value.beta.threads.messages.create.assert_called_once_with(
            thread_id="thread_id",
            role="user",
            content="foo bar\nfizz buzz",
        )
        mock_stream = mock_openai_client.return_value.beta.threads.runs.stream
        mock_stream.assert_called_once_with(
            thread_id="thread_id",
            assistant_id="assistant_id",
            event_handler=ANY,
        )

        assert result.value == "foo bar\nfoo bar"
        mock_event_handler.until_done.assert_called()
        mock_event_handler.get_final_messages.assert_called()
        assert mock_event_listener_handler.call_count == 5
