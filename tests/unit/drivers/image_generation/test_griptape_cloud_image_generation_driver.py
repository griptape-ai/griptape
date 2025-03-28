from unittest.mock import Mock

import pytest

from griptape.drivers.image_generation.griptape_cloud import GriptapeCloudImageGenerationDriver


class TestGriptapeCloudImageGenerationDriver:
    @pytest.fixture(autouse=True)
    def mock_post(self, mocker):
        def request(*args, **kwargs):
            mock_response = mocker.Mock()
            if "images/generations" in args[0]:
                mock_response.json.return_value = {
                    "artifact": {
                        "type": "ImageArtifact",
                        "width": 512,
                        "height": 512,
                        "format": "png",
                        "value": "aW1hZ2UgZGF0YQ==",
                        "meta": {"model": "dall-e-2", "prompt": "test prompt"},
                    },
                }
                return mock_response
            return mocker.Mock(
                raise_for_status=lambda: None,
            )

        return mocker.patch("requests.post", side_effect=request)

    @pytest.fixture()
    def driver(self):
        return GriptapeCloudImageGenerationDriver(model="dall-e-3", api_key="foo", quality="hd")

    def test_init(self, driver):
        assert driver

    def test_try_text_to_image(self, driver):
        image_artifact = driver.try_text_to_image(prompts=["test prompt"])

        assert image_artifact.value == b"image data"
        assert image_artifact.mime_type == "image/png"
        assert image_artifact.width == 512
        assert image_artifact.height == 512
        assert image_artifact.meta["model"] == "dall-e-2"
        assert image_artifact.meta["prompt"] == "test prompt"

    def test_try_image_variation(self, driver):
        with pytest.raises(NotImplementedError):
            driver.try_image_variation(prompts=[], image=Mock(value=b"image data"))

    def test_try_image_variation_invalid_size(self, driver):
        with pytest.raises(NotImplementedError):
            driver.try_image_variation(prompts=[], image=Mock(value=b"image data"))

    def test_try_image_variation_invalid_model(self, driver):
        with pytest.raises(NotImplementedError):
            driver.try_image_variation(prompts=[], image=Mock(value=b"image data"))

    def test_try_image_inpainting(self, driver):
        with pytest.raises(NotImplementedError):
            driver.try_image_inpainting(
                prompts=["test prompt"], image=Mock(value=b"image data"), mask=Mock(value=b"mask data")
            )
