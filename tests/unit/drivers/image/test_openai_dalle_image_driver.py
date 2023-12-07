from typing import Literal

import pytest
from unittest.mock import Mock
from griptape.drivers import OpenAiDalleImageGenerationDriver


class TestOpenAiDalleImageGenerationDriver:
    @pytest.fixture
    def driver(self):
        return OpenAiDalleImageGenerationDriver(model="dall-e-2", client=Mock(), quality="hd", image_size="512x512")

    def test_init(self, driver):
        assert driver

    def test_try_text_to_image(self, driver):
        driver.client.images.generate.return_value = Mock(data=[Mock(b64_json=b"aW1hZ2UgZGF0YQ==")])

        image_artifact = driver.try_text_to_image(prompts=["test prompt"])

        assert image_artifact.value == b"image data"
        assert image_artifact.mime_type == "image/png"
        assert image_artifact.width == 512
        assert image_artifact.height == 512
        assert image_artifact.model == "dall-e-2"
        assert image_artifact.prompt == "test prompt"
