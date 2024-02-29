import base64

import pytest

from griptape.artifacts import ImageArtifact
from griptape.drivers import BedrockStableDiffusionImageGenerationModelDriver


class TestBedrockStableDiffusionImageGenerationModelDriver:
    @pytest.fixture
    def model_driver(self):
        return BedrockStableDiffusionImageGenerationModelDriver()

    @pytest.fixture
    def image_artifact(self):
        return ImageArtifact(b"image", mime_type="image/png", width=1024, height=1024)

    @pytest.fixture
    def mask_artifact(self):
        return ImageArtifact(b"mask", mime_type="image/png", width=1024, height=1024)

    def test_init(self, model_driver):
        assert model_driver

    def test_text_to_image_request_parameters(self, model_driver):
        parameters = model_driver.text_to_image_request_parameters(
            ["prompt1", "prompt2"], 1024, 1024, negative_prompts=["nprompt1", "nprompt2"], seed=1234
        )

        assert isinstance(parameters, dict)
        assert parameters["seed"] == 1234
        assert parameters["width"] == 1024
        assert parameters["height"] == 1024
        assert parameters["text_prompts"] == [
            {"text": "prompt1", "weight": 1.0},
            {"text": "prompt2", "weight": 1.0},
            {"text": "nprompt1", "weight": -1.0},
            {"text": "nprompt2", "weight": -1.0},
        ]

    def test_image_variation_request_parameters(self, model_driver, image_artifact):
        parameters = model_driver.image_variation_request_parameters(
            ["prompt1", "prompt2"], image_artifact, negative_prompts=["nprompt1", "nprompt2"], seed=1234
        )

        assert isinstance(parameters, dict)
        assert parameters["seed"] == 1234
        assert parameters["width"] == image_artifact.width
        assert parameters["height"] == image_artifact.height
        assert parameters["text_prompts"] == [
            {"text": "prompt1", "weight": 1.0},
            {"text": "prompt2", "weight": 1.0},
            {"text": "nprompt1", "weight": -1.0},
            {"text": "nprompt2", "weight": -1.0},
        ]
        assert parameters["init_image"] == image_artifact.base64

    def test_image_inpainting_request_parameters(self, model_driver, image_artifact, mask_artifact):
        parameters = model_driver.image_inpainting_request_parameters(
            ["prompt1", "prompt2"], image_artifact, mask_artifact, negative_prompts=["nprompt1", "nprompt2"], seed=1234
        )

        assert isinstance(parameters, dict)
        assert parameters["seed"] == 1234
        assert parameters["width"] == image_artifact.width
        assert parameters["height"] == image_artifact.height
        assert parameters["text_prompts"] == [
            {"text": "prompt1", "weight": 1.0},
            {"text": "prompt2", "weight": 1.0},
            {"text": "nprompt1", "weight": -1.0},
            {"text": "nprompt2", "weight": -1.0},
        ]
        assert parameters["init_image"] == image_artifact.base64
        assert parameters["mask_image"] == mask_artifact.base64
        assert parameters["mask_source"] == "MASK_IMAGE_BLACK"

    def test_image_outpainting_request_parameters(self, model_driver, image_artifact, mask_artifact):
        parameters = model_driver.image_outpainting_request_parameters(
            ["prompt1", "prompt2"], image_artifact, mask_artifact, negative_prompts=["nprompt1", "nprompt2"], seed=1234
        )

        assert isinstance(parameters, dict)
        assert parameters["seed"] == 1234
        assert parameters["width"] == image_artifact.width
        assert parameters["height"] == image_artifact.height
        assert parameters["text_prompts"] == [
            {"text": "prompt1", "weight": 1.0},
            {"text": "prompt2", "weight": 1.0},
            {"text": "nprompt1", "weight": -1.0},
            {"text": "nprompt2", "weight": -1.0},
        ]
        assert parameters["init_image"] == image_artifact.base64
        assert parameters["mask_image"] == mask_artifact.base64
        assert parameters["mask_source"] == "MASK_IMAGE_WHITE"

    def test_get_generated_image_success(self, model_driver):
        image_bytes = b"image data"

        response = {"artifacts": [{"finishReason": "SUCCESS", "base64": base64.b64encode(image_bytes).decode("utf-8")}]}

        returned_image_bytes = model_driver.get_generated_image(response)

        assert image_bytes == returned_image_bytes

    def test_get_generated_image_content_filtered(self, model_driver):
        image_bytes = b"image data"

        response = {
            "artifacts": [{"finishReason": "CONTENT_FILTERED", "base64": base64.b64encode(image_bytes).decode("utf-8")}]
        }

        returned_image_bytes = model_driver.get_generated_image(response)

        assert image_bytes == returned_image_bytes

    def test_get_generated_image_failed(self, model_driver):
        image_bytes = b"image data"

        response = {"artifacts": [{"finishReason": "ERROR", "base64": base64.b64encode(image_bytes).decode("utf-8")}]}

        with pytest.raises(Exception):
            model_driver.get_generated_image(response)
