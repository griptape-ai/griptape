import io
from unittest.mock import Mock

import pytest

from griptape.drivers import AmazonBedrockImageGenerationDriver


class TestAmazonBedrockImageGenerationDriver:
    @pytest.fixture()
    def bedrock_client(self):
        return Mock()

    @pytest.fixture()
    def session(self, bedrock_client):
        session = Mock()
        session.client.return_value = bedrock_client

        return session

    @pytest.fixture()
    def model_driver(self):
        model_driver = Mock()
        model_driver.text_to_image_request_parameters.return_value = {}
        model_driver.get_generated_image.return_value = b"image data"

        return model_driver

    @pytest.fixture()
    def driver(self, session, model_driver):
        return AmazonBedrockImageGenerationDriver(
            session=session, model="stability.stable-diffusion-xl-v1", image_generation_model_driver=model_driver
        )

    def test_init(self, driver):
        assert driver

    def test_init_requires_image_generation_model_driver(self, session):
        with pytest.raises(TypeError):
            AmazonBedrockImageGenerationDriver(session=session, model="stability.stable-diffusion-xl-v1")  # pyright: ignore[reportCallIssue]

    def test_try_text_to_image(self, driver):
        driver.bedrock_client.invoke_model.return_value = {
            "body": io.BytesIO(
                b"""{
                        "artifacts": [
                            {
                                "finishReason": "SUCCESS",
                                "base64": "aW1hZ2UgZGF0YQ=="
                            }
                        ]
                    }"""
            )
        }

        image_artifact = driver.try_text_to_image(prompts=["test prompt"], negative_prompts=["test negative prompt"])

        assert image_artifact.value == b"image data"
        assert image_artifact.format == "png"
        assert image_artifact.mime_type == "image/png"
        assert image_artifact.width == 512
        assert image_artifact.height == 512
        assert image_artifact.meta["model"] == "stability.stable-diffusion-xl-v1"
        assert image_artifact.meta["prompt"] == "test prompt"
