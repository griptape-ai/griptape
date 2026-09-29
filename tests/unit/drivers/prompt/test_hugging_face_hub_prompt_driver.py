from unittest.mock import Mock

import pytest
from schema import Schema

from griptape.artifacts import (
    ActionArtifact,
    AudioArtifact,
    ImageArtifact,
    ImageUrlArtifact,
    ListArtifact,
    TextArtifact,
)
from griptape.common import (
    ActionCallMessageContent,
    ImageMessageContent,
    Message,
    PromptStack,
    TextDeltaMessageContent,
    TextMessageContent,
    ToolAction,
)
from griptape.drivers.prompt.huggingface_hub import HuggingFaceHubPromptDriver


class TestHuggingFaceHubPromptDriver:
    HUGGINGFACE_HUB_OUTPUT_SCHEMA = {
        "additionalProperties": False,
        "properties": {"foo": {"type": "string"}},
        "required": ["foo"],
        "type": "object",
    }
    HUGGINGFACE_HUB_RESPONSE_FORMAT = {
        "type": "json_schema",
        "json_schema": {"name": "Output", "schema": HUGGINGFACE_HUB_OUTPUT_SCHEMA, "strict": True},
    }

    @pytest.fixture(autouse=True)
    def mock_autotokenizer(self, mocker):
        mock_autotokenizer = mocker.patch("transformers.AutoTokenizer.from_pretrained").return_value
        mock_autotokenizer.model_max_length = 42
        return mock_autotokenizer

    @pytest.fixture()
    def mock_client(self, mocker):
        mock_client = mocker.patch("huggingface_hub.InferenceClient").return_value
        mock_client.chat_completion.return_value = Mock(
            choices=[Mock(message=Mock(content="model-output"))],
            usage=Mock(prompt_tokens=5, completion_tokens=10),
        )

        return mock_client

    @pytest.fixture()
    def mock_client_stream(self, mocker):
        mock_client = mocker.patch("huggingface_hub.InferenceClient").return_value
        mock_client.chat_completion.return_value = iter(
            [
                Mock(choices=[Mock(delta=Mock(content="model-output"))], usage=None),
                Mock(choices=[], usage=Mock(prompt_tokens=5, completion_tokens=10)),
            ]
        )

        return mock_client

    @pytest.fixture()
    def prompt_stack(self):
        prompt_stack = PromptStack()
        prompt_stack.output_schema = Schema({"foo": str})
        prompt_stack.add_system_message("system-input")
        prompt_stack.add_user_message("user-input")
        prompt_stack.add_assistant_message("assistant-input")
        return prompt_stack

    @pytest.fixture()
    def messages(self):
        return [
            {"role": "system", "content": "system-input"},
            {"role": "user", "content": "user-input"},
            {"role": "assistant", "content": "assistant-input"},
        ]

    def test_init(self):
        assert HuggingFaceHubPromptDriver(api_token="foobar", model="gpt2")

    def test_verify_structured_output_strategy(self):
        assert HuggingFaceHubPromptDriver(model="foo", api_token="bar", structured_output_strategy="native")

        with pytest.raises(
            ValueError, match="HuggingFaceHubPromptDriver does not support `tool` structured output strategy."
        ):
            HuggingFaceHubPromptDriver(model="foo", api_token="bar", structured_output_strategy="tool")

    @pytest.mark.parametrize("structured_output_strategy", ["native", "rule", "foo"])
    def test_try_run(self, prompt_stack, messages, mock_client, structured_output_strategy):
        # Given
        driver = HuggingFaceHubPromptDriver(
            api_token="api-token",
            model="repo-id",
            extra_params={"foo": "bar"},
            structured_output_strategy=structured_output_strategy,
        )

        # When
        message = driver.try_run(prompt_stack)

        # Then
        mock_client.chat_completion.assert_called_once_with(
            messages=messages,
            max_tokens=250,
            temperature=0.1,
            foo="bar",
            **(
                {"response_format": self.HUGGINGFACE_HUB_RESPONSE_FORMAT}
                if structured_output_strategy == "native"
                else {}
            ),
        )
        assert message.value == "model-output"
        assert message.usage.input_tokens == 5
        assert message.usage.output_tokens == 10

    def test_try_run_without_output_schema(self, prompt_stack, mock_client):
        # Given
        prompt_stack.output_schema = None
        driver = HuggingFaceHubPromptDriver(api_token="api-token", model="repo-id")

        # When
        driver.try_run(prompt_stack)

        # Then
        assert "response_format" not in mock_client.chat_completion.call_args.kwargs

    def test_try_run_does_not_send_stream_options(self, prompt_stack, mock_client):
        # Given
        driver = HuggingFaceHubPromptDriver(api_token="api-token", model="repo-id")

        # When
        driver.try_run(prompt_stack)

        # Then
        assert "stream_options" not in mock_client.chat_completion.call_args.kwargs

    def test_try_run_respects_max_tokens_and_temperature(self, prompt_stack, mock_client):
        # Given
        driver = HuggingFaceHubPromptDriver(api_token="api-token", model="repo-id", max_tokens=42, temperature=0.9)

        # When
        driver.try_run(prompt_stack)

        # Then
        assert mock_client.chat_completion.call_args.kwargs["max_tokens"] == 42
        assert mock_client.chat_completion.call_args.kwargs["temperature"] == 0.9

    def test_try_run_extra_params_override_defaults(self, prompt_stack, mock_client):
        # Given
        driver = HuggingFaceHubPromptDriver(
            api_token="api-token", model="repo-id", extra_params={"temperature": 1.0, "top_p": 0.5}
        )

        # When
        driver.try_run(prompt_stack)

        # Then
        assert mock_client.chat_completion.call_args.kwargs["temperature"] == 1.0
        assert mock_client.chat_completion.call_args.kwargs["top_p"] == 0.5

    def test_try_run_with_null_content(self, prompt_stack, mock_client):
        # Given
        mock_client.chat_completion.return_value = Mock(
            choices=[Mock(message=Mock(content=None))],
            usage=Mock(prompt_tokens=5, completion_tokens=10),
        )
        driver = HuggingFaceHubPromptDriver(api_token="api-token", model="repo-id")

        # When
        message = driver.try_run(prompt_stack)

        # Then
        assert message.value == ""
        assert message.usage.input_tokens == 5

    def test_try_run_with_no_usage(self, prompt_stack, mock_client):
        # Given
        mock_client.chat_completion.return_value = Mock(
            choices=[Mock(message=Mock(content="model-output"))],
            usage=None,
        )
        driver = HuggingFaceHubPromptDriver(api_token="api-token", model="repo-id")

        # When
        message = driver.try_run(prompt_stack)

        # Then
        assert message.value == "model-output"
        assert message.usage.input_tokens is None
        assert message.usage.output_tokens is None

    def test_try_run_throws_when_multiple_choices_returned(self, prompt_stack, mock_client):
        # Given
        mock_client.chat_completion.return_value = Mock(
            choices=[Mock(message=Mock(content="model-output"))] * 2,
            usage=Mock(prompt_tokens=5, completion_tokens=10),
        )
        driver = HuggingFaceHubPromptDriver(api_token="api-token", model="repo-id")

        # When / Then
        with pytest.raises(Exception, match="Completion with more than one choice is not supported yet."):
            driver.try_run(prompt_stack)

    def test_try_run_throws_when_no_choices_returned(self, prompt_stack, mock_client):
        # Given
        mock_client.chat_completion.return_value = Mock(choices=[], usage=None)
        driver = HuggingFaceHubPromptDriver(api_token="api-token", model="repo-id")

        # When / Then
        with pytest.raises(Exception, match="Completion with more than one choice is not supported yet."):
            driver.try_run(prompt_stack)

    @pytest.mark.parametrize("structured_output_strategy", ["native", "rule", "foo"])
    def test_try_stream(self, prompt_stack, messages, mock_client_stream, structured_output_strategy):
        # Given
        driver = HuggingFaceHubPromptDriver(
            api_token="api-token",
            model="repo-id",
            stream=True,
            extra_params={"foo": "bar"},
            structured_output_strategy=structured_output_strategy,
        )

        # When
        stream = driver.try_stream(prompt_stack)
        event = next(stream)

        # Then
        mock_client_stream.chat_completion.assert_called_once_with(
            messages=messages,
            max_tokens=250,
            temperature=0.1,
            stream_options={"include_usage": True},
            foo="bar",
            **(
                {"response_format": self.HUGGINGFACE_HUB_RESPONSE_FORMAT}
                if structured_output_strategy == "native"
                else {}
            ),
            stream=True,
        )
        assert isinstance(event.content, TextDeltaMessageContent)
        assert event.content.text == "model-output"
        assert event.content.index == 0

        event = next(stream)
        assert event.content is None
        assert event.usage.input_tokens == 5
        assert event.usage.output_tokens == 10

    def test_try_stream_skips_empty_choices_and_null_content(self, prompt_stack, mock_client_stream):
        # Given
        mock_client_stream.chat_completion.return_value = iter(
            [
                Mock(choices=[], usage=None),
                Mock(choices=[Mock(delta=Mock(content=None))], usage=None),
                Mock(choices=[Mock(delta=Mock(content="model-output"))], usage=None),
            ]
        )
        driver = HuggingFaceHubPromptDriver(api_token="api-token", model="repo-id", stream=True)

        # When
        events = list(driver.try_stream(prompt_stack))

        # Then
        assert len(events) == 1
        assert events[0].content.text == "model-output"

    def test_try_stream_emits_usage_on_every_reporting_chunk(self, prompt_stack, mock_client_stream):
        # Given
        mock_client_stream.chat_completion.return_value = iter(
            [
                Mock(choices=[Mock(delta=Mock(content="foo"))], usage=Mock(prompt_tokens=5, completion_tokens=1)),
                Mock(choices=[Mock(delta=Mock(content="bar"))], usage=Mock(prompt_tokens=5, completion_tokens=2)),
            ]
        )
        driver = HuggingFaceHubPromptDriver(api_token="api-token", model="repo-id", stream=True)

        # When
        events = list(driver.try_stream(prompt_stack))

        # Then
        usage_events = [event for event in events if event.usage.output_tokens is not None]
        assert [event.usage.output_tokens for event in usage_events] == [1, 2]

    def test_try_stream_with_no_usage(self, prompt_stack, mock_client_stream):
        # Given
        mock_client_stream.chat_completion.return_value = iter(
            [Mock(choices=[Mock(delta=Mock(content="model-output"))], usage=None)]
        )
        driver = HuggingFaceHubPromptDriver(api_token="api-token", model="repo-id", stream=True)

        # When
        events = list(driver.try_stream(prompt_stack))

        # Then
        assert len(events) == 1
        assert events[0].usage.input_tokens is None
        assert events[0].usage.output_tokens is None

    def test_try_run_with_images(self, mock_client):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.add_user_message(
            ListArtifact(
                [
                    TextArtifact("user-input"),
                    ImageArtifact(value=b"image-data", format="png", width=100, height=100),
                    ImageUrlArtifact(value="image-url"),
                ]
            )
        )
        driver = HuggingFaceHubPromptDriver(api_token="api-token", model="repo-id")

        # When
        driver.try_run(prompt_stack)

        # Then
        assert mock_client.chat_completion.call_args.kwargs["messages"] == [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "user-input"},
                    {"type": "image_url", "image_url": {"url": "data:image/png;base64,aW1hZ2UtZGF0YQ=="}},
                    {"type": "image_url", "image_url": {"url": "image-url"}},
                ],
            }
        ]

    def test_try_run_with_image_only(self, mock_client):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.add_user_message(ImageArtifact(value=b"image-data", format="png", width=100, height=100))
        driver = HuggingFaceHubPromptDriver(api_token="api-token", model="repo-id")

        # When
        driver.try_run(prompt_stack)

        # Then a lone image must not be flattened away into an empty string.
        assert mock_client.chat_completion.call_args.kwargs["messages"] == [
            {
                "role": "user",
                "content": [{"type": "image_url", "image_url": {"url": "data:image/png;base64,aW1hZ2UtZGF0YQ=="}}],
            }
        ]

    def test_try_run_with_image_url_only(self, mock_client):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.add_user_message(ImageUrlArtifact(value="https://example.com/image.png"))
        driver = HuggingFaceHubPromptDriver(api_token="api-token", model="repo-id")

        # When
        driver.try_run(prompt_stack)

        # Then
        assert mock_client.chat_completion.call_args.kwargs["messages"] == [
            {
                "role": "user",
                "content": [{"type": "image_url", "image_url": {"url": "https://example.com/image.png"}}],
            }
        ]

    def test_try_run_with_jpeg_image(self, mock_client):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.add_user_message(ImageArtifact(value=b"image-data", format="jpeg", width=100, height=100))
        driver = HuggingFaceHubPromptDriver(api_token="api-token", model="repo-id")

        # When
        driver.try_run(prompt_stack)

        # Then the mime type must follow the artifact format, not a hardcoded default.
        assert mock_client.chat_completion.call_args.kwargs["messages"][0]["content"][0]["image_url"]["url"].startswith(
            "data:image/jpeg;base64,"
        )

    def test_prompt_stack_to_messages_sends_text_only_messages_as_strings(self, prompt_stack, messages):
        # Given
        driver = HuggingFaceHubPromptDriver(api_token="api-token", model="repo-id")

        # When / Then
        assert driver._prompt_stack_to_messages(prompt_stack) == messages

    def test_prompt_stack_to_messages_joins_multiple_text_contents(self):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.add_user_message(ListArtifact([TextArtifact("foo"), TextArtifact("bar")]))
        driver = HuggingFaceHubPromptDriver(api_token="api-token", model="repo-id")

        # When / Then a multi-part but text-only message still collapses to a plain string.
        assert driver._prompt_stack_to_messages(prompt_stack) == [{"role": "user", "content": "foobar"}]

    def test_prompt_stack_to_messages_preserves_roles_for_image_messages(self):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.add_assistant_message(
            ImageArtifact(value=b"image-data", format="png", width=100, height=100),
        )
        driver = HuggingFaceHubPromptDriver(api_token="api-token", model="repo-id")

        # When / Then
        assert driver._prompt_stack_to_messages(prompt_stack)[0]["role"] == "assistant"

    def test_prompt_stack_to_messages_throws_for_unsupported_image_artifact(self):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.messages.append(
            Message(content=[ImageMessageContent(TextArtifact("not-an-image"))], role=Message.USER_ROLE)
        )
        driver = HuggingFaceHubPromptDriver(api_token="api-token", model="repo-id")

        # When / Then
        with pytest.raises(ValueError, match="Unsupported image artifact type"):
            driver._prompt_stack_to_messages(prompt_stack)

    def test_prompt_stack_to_messages_throws_for_audio_content(self):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.add_user_message(
            ListArtifact([TextArtifact("user-input"), AudioArtifact(value=b"audio-data", format="wav")])
        )
        driver = HuggingFaceHubPromptDriver(api_token="api-token", model="repo-id")

        # When / Then
        with pytest.raises(ValueError, match="Unsupported content type"):
            driver._prompt_stack_to_messages(prompt_stack)

    def test_prompt_stack_to_messages_throws_for_action_content(self):
        # Given
        prompt_stack = PromptStack()
        prompt_stack.messages.append(
            Message(
                content=[
                    TextMessageContent(TextArtifact("")),
                    ActionCallMessageContent(
                        ActionArtifact(ToolAction(tag="foo", name="Foo", path="bar", input={"baz": "qux"}))
                    ),
                ],
                role=Message.ASSISTANT_ROLE,
            )
        )
        driver = HuggingFaceHubPromptDriver(api_token="api-token", model="repo-id")

        # When / Then
        with pytest.raises(ValueError, match="Unsupported content type"):
            driver._prompt_stack_to_messages(prompt_stack)
