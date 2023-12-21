import io
from typing import Any
from unittest.mock import Mock

import pytest

from griptape.drivers import AmazonBedrockImageGenerationDriver, BaseImageGenerationModelDriver


class TestAmazonBedrockImageGenerationDriver:
    @pytest.fixture
    def bedrock_client(self):
        return Mock()

    @pytest.fixture
    def session(self, bedrock_client: Any):
        session = Mock()
        session.client.return_value = bedrock_client

        return session

    @pytest.fixture
    def model_driver(self):
        model_driver = Mock()
        model_driver.text_to_image_request_parameters.return_value = {}
        model_driver.get_generated_image.return_value = b"image data"

        return model_driver

    @pytest.fixture
    def driver(self, session: Any, model_driver: BaseImageGenerationModelDriver):
        return AmazonBedrockImageGenerationDriver(
            session=session, model="stability.stable-diffusion-xl-v1", image_generation_model_driver=model_driver
        )

    def test_init(self, driver: AmazonBedrockImageGenerationDriver):
        assert driver

    def test_init_requires_image_generation_model_driver(self, session: Any):
        with pytest.raises(TypeError):
            AmazonBedrockImageGenerationDriver(
                session=session, model="stability.stable-diffusion-xl-v1"
            )  # pyright: ignore

    def test_generate_image(self, driver: AmazonBedrockImageGenerationDriver):
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

        image_artifact = driver.generate_image(prompts=["test prompt"], negative_prompts=["test negative prompt"])

        assert image_artifact.value == b"image data"
        assert image_artifact.mime_type == "image/png"
        assert image_artifact.width == 512
        assert image_artifact.height == 512
        assert image_artifact.model == "stability.stable-diffusion-xl-v1"
        assert image_artifact.prompt == "test prompt"
