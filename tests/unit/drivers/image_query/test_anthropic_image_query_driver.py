import base64
from unittest.mock import Mock

import pytest

from griptape.artifacts import ImageArtifact
from griptape.drivers import AnthropicImageQueryDriver


class TestAnthropicImageQueryDriver:
    @pytest.fixture()
    def mock_client(self, mocker):
        mock_client = mocker.patch("anthropic.Anthropic")
        return_value = Mock(text="Content")
        mock_client.return_value.messages.create.return_value.content = [return_value]

        return mock_client

    @pytest.mark.parametrize(
        "model", [("claude-3-haiku-20240307"), ("claude-3-sonnet-20240229"), ("claude-3-opus-20240229")]
    )
    def test_init(self, model):
        assert AnthropicImageQueryDriver(model=model)

    def test_try_query(self, mock_client):
        driver = AnthropicImageQueryDriver(model="test-model")
        test_prompt_string = "Prompt String"
        test_binary_data = b"test-data"

        text_artifact = driver.try_query(
            test_prompt_string, [ImageArtifact(value=test_binary_data, width=100, height=100, format="png")]
        )

        expected_message = self._expected_message(test_binary_data, "image/png", test_prompt_string)

        mock_client.return_value.messages.create.assert_called_once_with(
            model=driver.model, max_tokens=256, messages=[expected_message]
        )

        assert text_artifact.value == "Content"

    def test_try_query_max_tokens_value(self, mock_client):
        driver = AnthropicImageQueryDriver(model="test-model", max_tokens=1024)
        test_prompt_string = "Prompt String"
        test_binary_data = b"test-data"

        text_artifact = driver.try_query(
            test_prompt_string, [ImageArtifact(value=test_binary_data, width=100, height=100, format="png")]
        )

        expected_message = self._expected_message(test_binary_data, "image/png", test_prompt_string)

        mock_client.return_value.messages.create.assert_called_once_with(
            model=driver.model, max_tokens=1024, messages=[expected_message]
        )

        assert text_artifact.value == "Content"

    def test_try_query_max_tokens_none(self, mock_client):
        driver = AnthropicImageQueryDriver(model="test-model", max_tokens=None)  # pyright: ignore[reportArgumentType]
        test_prompt_string = "Prompt String"
        test_binary_data = b"test-data"
        with pytest.raises(TypeError):
            driver.try_query(
                test_prompt_string, [ImageArtifact(value=test_binary_data, width=100, height=100, format="png")]
            )

    def test_try_query_wrong_media_type(self, mock_client):
        driver = AnthropicImageQueryDriver(model="test-model")
        test_prompt_string = "Prompt String"
        test_binary_data = b"test-data"

        # we expect this to pass Griptape code as the model will error appropriately
        text_artifact = driver.try_query(
            test_prompt_string, [ImageArtifact(value=test_binary_data, width=100, height=100, format="exr")]
        )

        expected_message = self._expected_message(test_binary_data, "image/exr", test_prompt_string)

        mock_client.return_value.messages.create.assert_called_once_with(
            model=driver.model, messages=[expected_message], max_tokens=256
        )

        assert text_artifact.value == "Content"

    def _expected_message(self, expected_data, expected_media_type, expected_prompt_string):
        encoded_data = base64.b64encode(expected_data).decode("utf-8")
        return {
            "content": [
                {
                    "source": {"data": encoded_data, "media_type": expected_media_type, "type": "base64"},
                    "type": "image",
                },
                {"text": expected_prompt_string, "type": "text"},
            ],
            "role": "user",
        }
