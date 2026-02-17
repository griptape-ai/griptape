from unittest.mock import Mock

import pytest

from griptape.drivers.image_generation.griptape_cloud import GriptapeCloudImageGenerationDriver


class TestGriptapeCloudImageGenerationDriver:
    @pytest.fixture(autouse=True)
    def mock_post(self, mocker):
        def request(*args, **kwargs):
            mock_response = mocker.Mock()
            if "images/generations" in args[0] or "images/variations" in args[0]:
                mock_response.json.return_value = {
                    "artifact": {
                        "type": "ImageArtifact",
                        "width": 1024,
                        "height": 1024,
                        "format": "png",
                        "value": "aW1hZ2UgZGF0YQ==",
                        "meta": {"model": "gpt-image-1-mini", "prompt": "test prompt"},
                    },
                }
                return mock_response
            return mocker.Mock(
                raise_for_status=lambda: None,
            )

        return mocker.patch("requests.post", side_effect=request)

    @pytest.fixture()
    def driver(self):
        return GriptapeCloudImageGenerationDriver(api_key="foo")

    @pytest.fixture()
    def gpt_image_1_mini_driver(self):
        return GriptapeCloudImageGenerationDriver(
            model="gpt-image-1-mini",
            api_key="foo",
            background="transparent",
            moderation="low",
            output_compression=0,
            output_format="png",
            image_size="1024x1024",
        )

    @pytest.fixture()
    def gpt_image_1_5_driver(self):
        return GriptapeCloudImageGenerationDriver(
            model="gpt-image-1.5",
            api_key="foo",
            quality="high",
            image_size="1024x1024",
        )

    def test_init(self, gpt_image_1_mini_driver, gpt_image_1_5_driver):
        assert gpt_image_1_mini_driver
        assert gpt_image_1_5_driver

    def test_default_model(self, driver):
        assert driver.model == "gpt-image-1-mini"

    def test_try_text_to_image_gpt_image_1_mini(self, gpt_image_1_mini_driver):
        image_artifact = gpt_image_1_mini_driver.try_text_to_image(prompts=["test prompt"])

        assert image_artifact.value == b"image data"
        assert image_artifact.mime_type == "image/png"
        assert image_artifact.width == 1024
        assert image_artifact.height == 1024
        assert image_artifact.meta["prompt"] == "test prompt"

    def test_try_text_to_image_gpt_image_1_5(self, gpt_image_1_5_driver):
        image_artifact = gpt_image_1_5_driver.try_text_to_image(prompts=["test prompt"])

        assert image_artifact.value == b"image data"
        assert image_artifact.mime_type == "image/png"
        assert image_artifact.width == 1024
        assert image_artifact.height == 1024
        assert image_artifact.meta["prompt"] == "test prompt"

    def test_invalid_image_size_landscape(self):
        with pytest.raises(ValueError):
            GriptapeCloudImageGenerationDriver(model="gpt-image-1-mini", api_key="foo", image_size="1792x1024")

    def test_invalid_image_size_portrait(self):
        with pytest.raises(ValueError):
            GriptapeCloudImageGenerationDriver(model="gpt-image-1-mini", api_key="foo", image_size="1024x1792")

    def test_try_image_variation_with_unsupported_model(self, driver):
        driver.model = "some-other-model"
        with pytest.raises(ValueError, match="Image variation is only supported with"):
            driver.try_image_variation(prompts=[], image=Mock(base64="aW1hZ2UgZGF0YQ=="))

    def test_try_image_variation_with_gpt_image_1_mini(self, gpt_image_1_mini_driver):
        image_artifact = gpt_image_1_mini_driver.try_image_variation(
            prompts=["test variation"], image=Mock(base64="aW1hZ2UgZGF0YQ==")
        )

        assert image_artifact.value == b"image data"
        assert image_artifact.mime_type == "image/png"
        assert image_artifact.width == 1024
        assert image_artifact.height == 1024

    def test_try_image_variation_with_gpt_image_1_5(self, gpt_image_1_5_driver):
        image_artifact = gpt_image_1_5_driver.try_image_variation(
            prompts=["test variation"], image=Mock(base64="aW1hZ2UgZGF0YQ==")
        )

        assert image_artifact.value == b"image data"
        assert image_artifact.mime_type == "image/png"
        assert image_artifact.width == 1024
        assert image_artifact.height == 1024

    def test_try_image_inpainting(self, driver):
        with pytest.raises(NotImplementedError):
            driver.try_image_inpainting(
                prompts=["test prompt"], image=Mock(value=b"image data"), mask=Mock(value=b"mask data")
            )
