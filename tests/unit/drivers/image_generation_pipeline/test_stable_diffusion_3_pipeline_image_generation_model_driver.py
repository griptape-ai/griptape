from unittest.mock import Mock, patch

import pytest
import torch
from PIL import Image

from griptape.drivers import StableDiffusion3ImageGenerationPipelineDriver


class TestStableDiffusion3PipelineImageGenerationModelDriver:
    @pytest.fixture()
    def model_driver(self):
        return StableDiffusion3ImageGenerationPipelineDriver()

    @pytest.fixture()
    def mock_import(self, monkeypatch):
        mock = Mock()
        monkeypatch.setattr(
            "griptape.drivers.image_generation_pipeline.stable_diffusion_3_image_generation_pipeline_driver.import_optional_dependency",
            mock,
        )

        return mock

    def test_prepare_pipeline_local_file(self, model_driver, mock_import):
        mock_sd3_pipeline = Mock()
        mock_import.return_value.StableDiffusion3Pipeline = mock_sd3_pipeline

        with patch("os.path.isfile", return_value=True):
            result = model_driver.prepare_pipeline("local_model", "cuda")

        mock_sd3_pipeline.from_single_file.assert_called_once_with("local_model")

        assert result == mock_sd3_pipeline.from_single_file.return_value
        result.to.assert_called_once_with("cuda")

    def test_prepare_pipeline_huggingface_model(self, model_driver, mock_import):
        mock_sd3_pipeline = Mock()
        mock_import.return_value.StableDiffusion3Pipeline = mock_sd3_pipeline

        with patch("os.path.isfile", return_value=False):
            result = model_driver.prepare_pipeline("huggingface/model", None)

        mock_sd3_pipeline.from_pretrained.assert_called_once_with("huggingface/model")
        assert result == mock_sd3_pipeline.from_pretrained.return_value
        result.to.assert_not_called()

    def test_prepare_pipeline_with_options(self, model_driver, mock_import):
        mock_sd3_pipeline = Mock()
        mock_import.return_value.StableDiffusion3Pipeline = mock_sd3_pipeline

        model_driver.torch_dtype = torch.float16
        model_driver.drop_t5_encoder = True
        model_driver.enable_model_cpu_offload = True

        result = model_driver.prepare_pipeline("huggingface/model", "cpu")

        mock_sd3_pipeline.from_pretrained.assert_called_once_with(
            "huggingface/model",
            torch_dtype=torch.float16,
            text_encoder_3=None,
            tokenizer_3=None,
        )
        assert result == mock_sd3_pipeline.from_pretrained.return_value
        result.to.assert_called_once_with("cpu")
        result.enable_model_cpu_offload.assert_called_once()

    def test_make_image_param(self, model_driver):
        assert model_driver.make_image_param(Mock(spec=Image.Image)) is None

    def test_make_additional_params(self, model_driver, mock_import):
        mock_torch = Mock()
        mock_import.return_value = mock_torch

        model_driver.guidance_scale = 7.5
        model_driver.steps = 50

        result = model_driver.make_additional_params(["no cats", "no dogs"], "cuda")

        expected = {
            "negative_prompt": "no cats, no dogs",
            "width": 1024,
            "height": 1024,
            "guidance_scale": 7.5,
            "num_inference_steps": 50,
        }

        assert result == expected

    def test_output_image_dimensions(self, model_driver):
        model_driver.width = 512
        model_driver.height = 768

        assert model_driver.output_image_dimensions == (512, 768)
