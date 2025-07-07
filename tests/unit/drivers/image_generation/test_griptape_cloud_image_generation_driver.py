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
                        "width": 1024,
                        "height": 1024,
                        "format": "png",
                        "value": "aW1hZ2UgZGF0YQ==",
                        "meta": {"model": "dall-e-3", "prompt": "test prompt"},
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
    def dall_e_3_driver(self):
        return GriptapeCloudImageGenerationDriver(
            model="dall-e-3", api_key="foo", style="vivid", quality="hd", image_size="1024x1024"
        )

    @pytest.fixture()
    def gpt_image_1_driver(self):
        return GriptapeCloudImageGenerationDriver(
            model="gpt-image-1",
            api_key="foo",
            background="transparent",
            moderation="low",
            output_compression=0,
            output_format="png",
            image_size="1024x1024",
        )

    def test_init(self, dall_e_3_driver, gpt_image_1_driver):
        assert dall_e_3_driver
        assert gpt_image_1_driver

    def test_try_text_to_image_dall_e_3(self, dall_e_3_driver):
        image_artifact = dall_e_3_driver.try_text_to_image(prompts=["test prompt"])

        assert image_artifact.value == b"image data"
        assert image_artifact.mime_type == "image/png"
        assert image_artifact.width == 1024
        assert image_artifact.height == 1024
        assert image_artifact.meta["prompt"] == "test prompt"

    def test_try_text_to_image_gpt_image_1(self, gpt_image_1_driver):
        image_artifact = gpt_image_1_driver.try_text_to_image(prompts=["test prompt"])

        assert image_artifact.value == b"image data"
        assert image_artifact.mime_type == "image/png"
        assert image_artifact.width == 1024
        assert image_artifact.height == 1024
        assert image_artifact.meta["prompt"] == "test prompt"

    def test_dall_e_3_driver_background(self):
        driver = GriptapeCloudImageGenerationDriver(model="dall-e-3", api_key="foo", background="transparent")
        assert "background" not in driver._build_model_params()

    def test_dall_e_3_driver_moderation(self):
        driver = GriptapeCloudImageGenerationDriver(model="dall-e-3", api_key="foo", moderation="low")
        assert "moderation" not in driver._build_model_params()

    def test_dall_e_3_driver_output_compression(self):
        driver = GriptapeCloudImageGenerationDriver(model="dall-e-3", api_key="foo", output_compression=0)
        assert "output_compression" not in driver._build_model_params()

    def test_dall_e_3_driver_output_format(self):
        driver = GriptapeCloudImageGenerationDriver(model="dall-e-3", api_key="foo", output_format="png")
        assert "output_format" not in driver._build_model_params()

    def test_dall_e_3_driver_landscape(self):
        with pytest.raises(ValueError):
            GriptapeCloudImageGenerationDriver(model="dall-e-3", api_key="foo", image_size="1536x1024")

    def test_dall_e_3_driver_portrait(self):
        with pytest.raises(ValueError):
            GriptapeCloudImageGenerationDriver(model="dall-e-3", api_key="foo", image_size="1024x1536")

    def test_gpt_image_1_driver_style(self):
        driver = GriptapeCloudImageGenerationDriver(model="gpt-image-1", api_key="foo", style="vivid")
        assert "style" not in driver._build_model_params()

    def test_gpt_image_1_driver_quality(self):
        driver = GriptapeCloudImageGenerationDriver(model="gpt-image-1", api_key="foo", quality="hd")
        assert "quality" not in driver._build_model_params()

    def test_gpt_image_1_driver_landscape(self):
        with pytest.raises(ValueError):
            GriptapeCloudImageGenerationDriver(model="gpt-image-1", api_key="foo", image_size="1792x1024")

    def test_gpt_image_1_driver_portrait(self):
        with pytest.raises(ValueError):
            GriptapeCloudImageGenerationDriver(model="gpt-image-1", api_key="foo", image_size="1024x1792")

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
