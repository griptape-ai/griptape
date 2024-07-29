import io
from unittest.mock import Mock

import pytest
from PIL import Image

from griptape.artifacts import ImageArtifact
from griptape.drivers import (
    BaseDiffusionImageGenerationPipelineDriver,
    HuggingFacePipelineImageGenerationDriver,
)


class TestHuggingFacePipelineImageGenerationDriver:
    @pytest.fixture()
    def image_artifact(self):
        buffer = io.BytesIO()
        Image.new("RGB", (256, 256)).save(buffer, "PNG")
        return ImageArtifact(buffer.getvalue(), format="png", width=256, height=256)

    @pytest.fixture()
    def model_driver(self):
        model_driver = Mock(spec=BaseDiffusionImageGenerationPipelineDriver)
        mock_pipeline = Mock()
        mock_pipeline.return_value = Mock()
        mock_pipeline.return_value.images = [Image.new("RGB", (256, 256))]
        model_driver.prepare_pipeline.return_value = mock_pipeline
        model_driver.make_image_param.return_value = {"image": Image.new("RGB", (256, 256))}
        model_driver.make_additional_params.return_value = {"negative_prompt": ["sample negative prompt"]}
        model_driver.output_image_dimensions = (256, 256)

        return model_driver

    @pytest.fixture()
    def driver(self, model_driver):
        return HuggingFacePipelineImageGenerationDriver(model="repo/model", pipeline_driver=model_driver)

    def test_init(self, driver):
        assert driver

    def test_try_text_to_image(self, driver):
        image_artifact = driver.try_text_to_image(prompts=["test prompt"])

        assert image_artifact
        assert image_artifact.mime_type == "image/png"
        assert image_artifact.width == 256
        assert image_artifact.height == 256

    def test_try_image_variation(self, driver, image_artifact):
        image_artifact = driver.try_image_variation(prompts=["test prompt"], image=image_artifact)

        assert image_artifact
        assert image_artifact.mime_type == "image/png"
        assert image_artifact.width == 256
        assert image_artifact.height == 256

    def test_try_image_inpainting(self, driver):
        with pytest.raises(NotImplementedError):
            driver.try_image_inpainting(prompts=["test prompt"], image=Mock(), mask=Mock())

    def test_try_image_outpainting(self, driver):
        with pytest.raises(NotImplementedError):
            driver.try_image_outpainting(prompts=["test prompt"], image=Mock(), mask=Mock())

    def test_configurable_output_format(self, driver):
        driver.output_format = "jpeg"
        image_artifact = driver.try_text_to_image(prompts=["test prompt"])

        assert image_artifact
        assert image_artifact.mime_type == "image/jpeg"
        assert image_artifact.width == 256
        assert image_artifact.height == 256
