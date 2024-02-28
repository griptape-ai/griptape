import pytest
from unittest.mock import Mock
from griptape.drivers import OpenAiImageGenerationDriver


class TestOpenAiImageGenerationDriver:
    @pytest.fixture
    def driver(self):
        return OpenAiImageGenerationDriver(model="dall-e-2", client=Mock(), quality="hd", image_size="512x512")

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

    def test_try_image_variation(self, driver):
        driver.client.images.create_variation.return_value = Mock(data=[Mock(b64_json=b"aW1hZ2UgZGF0YQ==")])

        image_artifact = driver.try_image_variation(prompts=[], image=Mock(value=b"image data"))

        assert image_artifact.value == b"image data"
        assert image_artifact.mime_type == "image/png"
        assert image_artifact.width == 512
        assert image_artifact.height == 512
        assert image_artifact.model == "dall-e-2"

    def test_try_image_variation_invalid_size(self, driver):
        driver.image_size = "1024x1792"

        with pytest.raises(ValueError):
            driver.try_image_variation(prompts=[], image=Mock(value=b"image data"))

    def test_try_image_variation_invalid_model(self, driver):
        driver.model = "dall-e-3"

        with pytest.raises(NotImplementedError):
            driver.try_image_variation(prompts=[], image=Mock(value=b"image data"))

    def test_try_image_inpainting(self, driver):
        driver.client.images.edit.return_value = Mock(data=[Mock(b64_json=b"aW1hZ2UgZGF0YQ==")])

        image_artifact = driver.try_image_inpainting(
            prompts=["test prompt"], image=Mock(value=b"image data"), mask=Mock(value=b"mask data")
        )

        assert image_artifact.value == b"image data"
        assert image_artifact.mime_type == "image/png"
        assert image_artifact.width == 512
        assert image_artifact.height == 512
        assert image_artifact.model == "dall-e-2"
        assert image_artifact.prompt == "test prompt"

    def test_try_image_inpainting_invalid_size(self, driver):
        driver.image_size = "1024x1792"

        with pytest.raises(ValueError):
            driver.try_image_variation(prompts=[], image=Mock(value=b"image data"))

    def test_try_image_inpainting_invalid_model(self, driver):
        driver.model = "dall-e-3"

        with pytest.raises(NotImplementedError):
            driver.try_image_variation(prompts=[], image=Mock(value=b"image data"))
