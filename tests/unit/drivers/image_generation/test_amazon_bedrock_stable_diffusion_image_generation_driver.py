import io
from unittest.mock import Mock

import pytest
from botocore.response import StreamingBody

from griptape.drivers import AmazonBedrockStableDiffusionImageGenerationDriver


class TestAmazonBedrockStableDiffusionImageGenerationDriver:
    @pytest.fixture
    def bedrock_client(self):
        return Mock()

    @pytest.fixture
    def session(self, bedrock_client):
        session = Mock()
        session.client.return_value = bedrock_client

        return session

    @pytest.fixture
    def driver(self, session):
        return AmazonBedrockStableDiffusionImageGenerationDriver(
            session=session, model="stability.stable-diffusion-xl-v1"
        )

    def test_init(self, driver):
        assert driver

    def test_generate_image(self, driver):
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
