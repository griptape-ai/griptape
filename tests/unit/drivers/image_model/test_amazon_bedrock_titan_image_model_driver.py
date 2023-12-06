import pytest

from griptape.drivers import AmazonBedrockTitanImageModelDriver


class TestAmazonBedrockTitanImageModelDriver:
    @pytest.fixture
    def model_driver(self):
        return AmazonBedrockTitanImageModelDriver()

    def test_init(self, model_driver):
        assert model_driver

    def test_text_to_image_request_parameters(self, model_driver):
        parameters = model_driver.text_to_image_request_parameters(
            ["prompt1", "prompt2"], 1024, 1024, negative_prompts=["nprompt1", "nprompt2"], seed=1234
        )

        assert isinstance(parameters, dict)
        assert "taskType" in parameters
        assert parameters["taskType"] == "TEXT_IMAGE"
        assert "textToImageParams" in parameters
        assert parameters["textToImageParams"] == {"text": "prompt1, prompt2", "negativeText": "nprompt1, nprompt2"}
        assert "imageGenerationConfig" in parameters
        assert parameters["imageGenerationConfig"]["numberOfImages"] == 1
        assert parameters["imageGenerationConfig"]["width"] == 1024
        assert parameters["imageGenerationConfig"]["height"] == 1024
        assert parameters["imageGenerationConfig"]["seed"] == 1234
