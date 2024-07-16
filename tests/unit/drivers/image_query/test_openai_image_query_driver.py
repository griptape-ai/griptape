from unittest.mock import Mock

import pytest

from griptape.artifacts import ImageArtifact
from griptape.drivers import OpenAiImageQueryDriver


class TestOpenAiVisionImageQueryDriver:
    @pytest.fixture()
    def mock_completion_create(self, mocker):
        mock_chat_create = mocker.patch("openai.OpenAI").return_value.chat.completions.create
        mock_choice = Mock(message=Mock(content="expected_output_text"))
        mock_chat_create.return_value.choices = [mock_choice]
        return mock_chat_create

    def test_init(self):
        assert OpenAiImageQueryDriver(model="gpt-4-vision-preview")

    def test_try_query_defaults(self, mock_completion_create):
        driver = OpenAiImageQueryDriver(model="gpt-4-vision-preview")
        test_prompt_string = "Prompt String"
        test_binary_data = b"test-data"
        test_image = ImageArtifact(value=test_binary_data, width=100, height=100, format="png")
        text_artifact = driver.try_query(test_prompt_string, [test_image])

        messages = self._expected_messages(test_prompt_string, test_image.base64)

        mock_completion_create.assert_called_once_with(model=driver.model, messages=[messages], max_tokens=256)

        assert text_artifact.value == "expected_output_text"

    def test_try_query_max_tokens(self, mock_completion_create):
        driver = OpenAiImageQueryDriver(model="gpt-4-vision-preview", max_tokens=1024)
        test_prompt_string = "Prompt String"
        test_binary_data = b"test-data"
        test_image = ImageArtifact(value=test_binary_data, width=100, height=100, format="png")
        driver.try_query(test_prompt_string, [test_image])

        messages = self._expected_messages(test_prompt_string, test_image.base64)

        mock_completion_create.assert_called_once_with(model=driver.model, messages=[messages], max_tokens=1024)

    def test_try_query_multiple_choices(self, mock_completion_create):
        mock_completion_create.return_value.choices.append(Mock(message=Mock(content="expected_output_text2")))
        driver = OpenAiImageQueryDriver(model="gpt-4-vision-preview")

        with pytest.raises(Exception, match="Image query responses with more than one choice are not supported yet."):
            driver.try_query("Prompt String", [ImageArtifact(value=b"test-data", width=100, height=100, format="png")])

    def _expected_messages(self, expected_prompt_string, expected_binary_data):
        return {
            "content": [
                {"type": "text", "text": expected_prompt_string},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{expected_binary_data}", "detail": "auto"},
                },
            ],
            "role": "user",
        }
