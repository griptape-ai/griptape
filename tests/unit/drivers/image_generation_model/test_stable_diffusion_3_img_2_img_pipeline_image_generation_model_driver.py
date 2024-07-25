from unittest.mock import Mock, patch

import pytest
from PIL import Image

from griptape.drivers.image_generation_model.stable_diffusion_3_img_2_img_pipeline_image_generation_model_driver import (
    StableDiffusion3Img2ImgPipelineImageGenerationModelDriver,
)


class TestStableDiffusion3Img2ImgPipelineImageGenerationModelDriver:
    @pytest.fixture()
    def model_driver(self):
        return StableDiffusion3Img2ImgPipelineImageGenerationModelDriver()

    @pytest.fixture()
    def mock_import(self, monkeypatch):
        mock = Mock()
        monkeypatch.setattr(
            "griptape.drivers.image_generation_model.stable_diffusion_3_img_2_img_pipeline_image_generation_model_driver.import_optional_dependency",
            mock,
        )

        return mock

    def test_prepare_pipeline_local_file(self, model_driver, mock_import):
        mock_sd3_img2img_pipeline = Mock()
        mock_import.return_value.StableDiffusion3Img2ImgPipeline = mock_sd3_img2img_pipeline

        with patch("os.path.isfile", return_value=True), pytest.raises(NotImplementedError):
            model_driver.prepare_pipeline("local_model", "cuda")

    def test_prepare_pipeline_huggingface_model(self, model_driver, mock_import):
        mock_sd3_img2img_pipeline = Mock()
        mock_import.return_value.StableDiffusion3Img2ImgPipeline = mock_sd3_img2img_pipeline

        with patch("os.path.isfile", return_value=False):
            result = model_driver.prepare_pipeline("huggingface/model", "cuda")

        mock_sd3_img2img_pipeline.from_pretrained.assert_called_once_with("huggingface/model")

        assert result == mock_sd3_img2img_pipeline.from_pretrained.return_value
        result.to.assert_called_once_with("cuda")

    def test_make_image_param(self, model_driver):
        mock_image = Mock(spec=Image.Image)
        result = model_driver.make_image_param(mock_image)
        assert result == {"image": mock_image}

    def test_make_image_param_without_image(self, model_driver):
        with pytest.raises(ValueError):
            model_driver.make_image_param(None)

    def test_make_additional_params(self, model_driver, mock_import):
        mock_torch = Mock()
        mock_import.return_value = mock_torch

        model_driver.guidance_scale = 7.5
        model_driver.steps = 50
        model_driver.strength = 0.75

        result = model_driver.make_additional_params(["no cats", "no dogs"], "cuda")

        expected = {
            "negative_prompt": "no cats, no dogs",
            "guidance_scale": 7.5,
            "num_inference_steps": 50,
            "strength": 0.75,
        }

        assert result == expected
        assert "height" not in result
        assert "width" not in result

    def test_get_output_image_dimensions(self, model_driver):
        model_driver.width = 512
        model_driver.height = 768

        dimensions = model_driver.output_image_dimensions()

        assert dimensions == (512, 768)
