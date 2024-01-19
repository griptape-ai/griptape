import pytest

from griptape.artifacts import ImageArtifact
from griptape.drivers import BedrockTitanImageGenerationModelDriver


class TestBedrockTitanImageGenerationModelDriver:
    @pytest.fixture
    def model_driver(self):
        return BedrockTitanImageGenerationModelDriver()

    @pytest.fixture
    def image_artifact(self):
        return ImageArtifact(b"image", mime_type="image/png", width=1024, height=512)

    @pytest.fixture
    def mask_artifact(self):
        return ImageArtifact(b"mask", mime_type="image/png", width=1024, height=512)

    def test_init(self, model_driver):
        assert model_driver

    def test_text_to_image_request_parameters(self, model_driver):
        parameters = model_driver.text_to_image_request_parameters(
            ["prompt1", "prompt2"], 1024, 512, negative_prompts=["nprompt1", "nprompt2"], seed=1234
        )

        assert isinstance(parameters, dict)
        assert "taskType" in parameters
        assert parameters["taskType"] == "TEXT_IMAGE"
        assert "textToImageParams" in parameters
        assert parameters["textToImageParams"] == {"text": "prompt1, prompt2", "negativeText": "nprompt1, nprompt2"}
        assert parameters["textToImageParams"]["negativeText"] == "nprompt1, nprompt2"
        assert "imageGenerationConfig" in parameters
        assert parameters["imageGenerationConfig"]["numberOfImages"] == 1
        assert parameters["imageGenerationConfig"]["width"] == 1024
        assert parameters["imageGenerationConfig"]["height"] == 512
        assert parameters["imageGenerationConfig"]["seed"] == 1234

    def test_image_variation_request_parameters(self, model_driver, image_artifact):
        parameters = model_driver.image_variation_request_parameters(
            ["prompt1", "prompt2"], image_artifact, negative_prompts=["nprompt1", "nprompt2"], seed=1234
        )

        assert isinstance(parameters, dict)
        assert "taskType" in parameters
        assert parameters["taskType"] == "IMAGE_VARIATION"
        assert "imageVariationParams" in parameters
        assert parameters["imageVariationParams"]["text"] == "prompt1, prompt2"
        assert parameters["imageVariationParams"]["images"] == [image_artifact.base64]
        assert parameters["imageVariationParams"]["negativeText"] == "nprompt1, nprompt2"
        assert "imageGenerationConfig" in parameters
        assert parameters["imageGenerationConfig"]["numberOfImages"] == 1
        assert parameters["imageGenerationConfig"]["width"] == 1024
        assert parameters["imageGenerationConfig"]["height"] == 512
        assert parameters["imageGenerationConfig"]["seed"] == 1234

    def test_image_inpainting_request_parameters(self, model_driver, image_artifact, mask_artifact):
        parameters = model_driver.image_inpainting_request_parameters(
            ["prompt1", "prompt2"], image_artifact, mask_artifact, negative_prompts=["nprompt1", "nprompt2"], seed=1234
        )

        assert isinstance(parameters, dict)
        assert "taskType" in parameters
        assert parameters["taskType"] == "INPAINTING"
        assert "inPaintingParams" in parameters
        assert parameters["inPaintingParams"]["text"] == "prompt1, prompt2"
        assert parameters["inPaintingParams"]["image"] == image_artifact.base64
        assert parameters["inPaintingParams"]["maskImage"] == mask_artifact.base64
        assert parameters["inPaintingParams"]["negativeText"] == "nprompt1, nprompt2"
        assert "imageGenerationConfig" in parameters
        assert parameters["imageGenerationConfig"]["numberOfImages"] == 1
        assert parameters["imageGenerationConfig"]["width"] == 1024
        assert parameters["imageGenerationConfig"]["height"] == 512
        assert parameters["imageGenerationConfig"]["seed"] == 1234

    def test_image_outpainting_request_parameters(self, model_driver, image_artifact, mask_artifact):
        parameters = model_driver.image_outpainting_request_parameters(
            ["prompt1", "prompt2"], image_artifact, mask_artifact, negative_prompts=["nprompt1", "nprompt2"], seed=1234
        )

        assert isinstance(parameters, dict)
        assert "taskType" in parameters
        assert parameters["taskType"] == "OUTPAINTING"
        assert "outPaintingParams" in parameters
        assert parameters["outPaintingParams"]["text"] == "prompt1, prompt2"
        assert parameters["outPaintingParams"]["image"] == image_artifact.base64
        assert parameters["outPaintingParams"]["maskImage"] == mask_artifact.base64
        assert parameters["outPaintingParams"]["negativeText"] == "nprompt1, nprompt2"
        assert "imageGenerationConfig" in parameters
        assert parameters["imageGenerationConfig"]["numberOfImages"] == 1
        assert parameters["imageGenerationConfig"]["width"] == 1024
        assert parameters["imageGenerationConfig"]["height"] == 512
        assert parameters["imageGenerationConfig"]["seed"] == 1234
