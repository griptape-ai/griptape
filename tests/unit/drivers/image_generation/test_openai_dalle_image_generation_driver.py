import pytest
from unittest.mock import Mock
from griptape.drivers import OpenAiDalleImageGenerationDriver


class TestOpenAiDalleImageGenerationDriver:
    @pytest.fixture
    def driver(self) -> OpenAiDalleImageGenerationDriver:
        return OpenAiDalleImageGenerationDriver(model="dall-e-2", client=Mock(), quality="hd", image_size="512x512")

    def test_init(self, driver: OpenAiDalleImageGenerationDriver) -> None:
        assert driver

    def test_generate_image(self, driver: OpenAiDalleImageGenerationDriver) -> None:
        driver.client.images.generate.return_value = Mock(data=[Mock(b64_json=b"aW1hZ2UgZGF0YQ==")])  # pyright: ignore

        image_artifact = driver.generate_image(prompts=["test prompt"])

        assert image_artifact.value == b"image data"
        assert image_artifact.mime_type == "image/png"
        assert image_artifact.width == 512
        assert image_artifact.height == 512
        assert image_artifact.model == "dall-e-2"
        assert image_artifact.prompt == "test prompt"
