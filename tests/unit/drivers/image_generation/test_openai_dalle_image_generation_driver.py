from unittest.mock import Mock

import openai
import pytest

from griptape.drivers import OpenAiDalleImageGenerationDriver


class TestOpenAiDalleImageGenerationDriver:
    @pytest.fixture
    def driver(self):
        return OpenAiDalleImageGenerationDriver()

    def test_init(self, driver):
        assert driver

    def test_make_request(self, driver):
        test_url = "image url"

        openai.Image.create = Mock(return_value={"data": [{"url": test_url}]})

        image_url = driver._make_request(prompt="test prompt")

        assert image_url == test_url

    def test_download_image(self, driver):
        driver.requests_session.get = Mock(return_value=Mock(content=b"image data"))

        image_data = driver._download_image(url="test url")

        assert image_data == b"image data"

    def test_generate_image(self, driver):
        driver._make_request = Mock(return_value="test url")
        driver._download_image = Mock(return_value=b"image data")

        image_artifact = driver.generate_image(prompts=["test prompt"])

        assert image_artifact.value == b"image data"
        assert image_artifact.mime_type == "image/png"
        assert image_artifact.width == 512
        assert image_artifact.height == 512
        assert image_artifact.model == "openai/dalle2"
        assert image_artifact.prompt == "test prompt"
