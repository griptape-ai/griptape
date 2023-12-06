import pytest

from griptape.drivers import AmazonBedrockStableDiffusionImageModelDriver


class TestAmazonBedrockStableDiffusionImageModelDriver:
    @pytest.fixture
    def model_driver(self):
        return AmazonBedrockStableDiffusionImageModelDriver()

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
