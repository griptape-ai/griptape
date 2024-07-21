import pytest

from griptape.artifacts import ImageArtifact
from griptape.drivers import DummyImageGenerationDriver
from griptape.exceptions import DummyError


class TestDummyImageGenerationDriver:
    @pytest.fixture()
    def image_generation_driver(self):
        return DummyImageGenerationDriver()

    def test_init(self, image_generation_driver):
        assert image_generation_driver

    def test_text_to_image(self, image_generation_driver):
        with pytest.raises(DummyError):
            image_generation_driver.try_text_to_image("prompt-stack")

    def test_try_image_variation(self, image_generation_driver):
        with pytest.raises(DummyError):
            image_generation_driver.try_image_variation(
                "prompt-stack",
                ImageArtifact(value=b"", width=100, height=100, format="png"),
                ImageArtifact(value=b"", width=100, height=100, format="png"),
            )

    def test_try_image_inpainting(self, image_generation_driver):
        with pytest.raises(DummyError):
            image_generation_driver.try_image_inpainting(
                "prompt-stack",
                ImageArtifact(value=b"", width=100, height=100, format="png"),
                ImageArtifact(value=b"", width=100, height=100, format="png"),
            )

    def test_try_image_outpainting(self, image_generation_driver):
        with pytest.raises(DummyError):
            image_generation_driver.try_image_outpainting(
                "prompt-stack",
                ImageArtifact(value=b"", width=100, height=100, format="png"),
                ImageArtifact(value=b"", width=100, height=100, format="png"),
            )
