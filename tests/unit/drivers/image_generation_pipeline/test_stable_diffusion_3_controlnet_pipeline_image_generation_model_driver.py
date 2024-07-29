from unittest.mock import Mock, patch

import pytest
import torch
from PIL import Image

from griptape.drivers import StableDiffusion3ControlNetImageGenerationPipelineDriver


class TestStableDiffusion3ControlNetPipelineImageGenerationModelDriver:
    @pytest.fixture()
    def model_driver(self):
        return StableDiffusion3ControlNetImageGenerationPipelineDriver(controlnet_model="controlnet_model")

    @pytest.fixture()
    def mock_import(self, monkeypatch):
        mock = Mock()
        monkeypatch.setattr(
            "griptape.drivers.image_generation_pipeline.stable_diffusion_3_controlnet_image_generation_pipeline_driver.import_optional_dependency",
            mock,
        )

        return mock

    def test_prepare_pipeline_local_file(self, model_driver, mock_import):
        mock_sd3_controlnet_model = Mock()
        mock_sd3_controlnet_pipeline = Mock()
        mock_import.side_effect = [
            Mock(SD3ControlNetModel=mock_sd3_controlnet_model),
            Mock(StableDiffusion3ControlNetPipeline=mock_sd3_controlnet_pipeline),
        ]

        with patch("os.path.isfile", return_value=True):
            result = model_driver.prepare_pipeline("local_model", "cuda")

        mock_sd3_controlnet_model.from_single_file.assert_called_once_with("controlnet_model")
        mock_sd3_controlnet_pipeline.from_single_file.assert_called_once_with(
            "local_model", controlnet=mock_sd3_controlnet_model.from_single_file.return_value
        )

        assert result == mock_sd3_controlnet_pipeline.from_single_file.return_value
        result.to.assert_called_once_with("cuda")

    def test_prepare_pipeline_huggingface_model(self, model_driver, mock_import):
        mock_sd3_controlnet_model = Mock()
        mock_sd3_controlnet_pipeline = Mock()
        mock_import.side_effect = [
            Mock(SD3ControlNetModel=mock_sd3_controlnet_model),
            Mock(StableDiffusion3ControlNetPipeline=mock_sd3_controlnet_pipeline),
        ]

        with patch("os.path.isfile", return_value=False):
            result = model_driver.prepare_pipeline("huggingface/model", "cuda")

        mock_sd3_controlnet_model.from_pretrained.assert_called_once_with("controlnet_model")
        mock_sd3_controlnet_pipeline.from_pretrained.assert_called_once_with(
            "huggingface/model", controlnet=mock_sd3_controlnet_model.from_pretrained.return_value
        )

        assert result == mock_sd3_controlnet_pipeline.from_pretrained.return_value
        result.to.assert_called_once_with("cuda")

    def test_prepare_pipeline_with_options(self, model_driver, mock_import):
        mock_sd3_controlnet_model = Mock()
        mock_sd3_controlnet_pipeline = Mock()
        mock_import.side_effect = [
            Mock(SD3ControlNetModel=mock_sd3_controlnet_model),
            Mock(StableDiffusion3ControlNetPipeline=mock_sd3_controlnet_pipeline),
        ]

        model_driver.torch_dtype = torch.float16
        model_driver.drop_t5_encoder = True
        model_driver.enable_model_cpu_offload = True

        result = model_driver.prepare_pipeline("huggingface/model", "cpu")

        mock_sd3_controlnet_pipeline.from_pretrained.assert_called_once_with(
            "huggingface/model",
            controlnet=mock_sd3_controlnet_model.from_pretrained.return_value,
            torch_dtype=torch.float16,
            text_encoder_3=None,
            tokenizer_3=None,
        )

        assert result == mock_sd3_controlnet_pipeline.from_pretrained.return_value
        result.to.assert_called_once_with("cpu")
        result.enable_model_cpu_offload.assert_called_once()

    def test_make_image_param(self, model_driver):
        mock_image = Mock(spec=Image.Image)
        result = model_driver.make_image_param(mock_image)

        assert result == {"control_image": mock_image}

    def test_make_image_param_without_image(self, model_driver):
        with pytest.raises(ValueError):
            model_driver.make_image_param(None)

    def test_make_additional_params(self, model_driver, mock_import):
        mock_torch = Mock()
        mock_import.return_value = mock_torch

        model_driver.guidance_scale = 7.5
        model_driver.steps = 50
        model_driver.controlnet_conditioning_scale = 0.8

        result = model_driver.make_additional_params(["no cats", "no dogs"], "cuda")

        expected = {
            "negative_prompt": "no cats, no dogs",
            "guidance_scale": 7.5,
            "num_inference_steps": 50,
            "controlnet_conditioning_scale": 0.8,
        }

        assert result == expected
        assert "height" not in result
        assert "width" not in result

    def test_output_image_dimensions(self, model_driver):
        model_driver.width = 512
        model_driver.height = 768

        dimensions = model_driver.output_image_dimensions

        assert dimensions == (512, 768)
