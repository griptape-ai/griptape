import os
import tempfile
import unittest
import uuid
from unittest.mock import Mock

import pytest

from griptape.tools import ImageGenerator


class TestImageGenerator:
    @pytest.fixture
    def image_generation_engine(self):
        return Mock()

    @pytest.fixture
    def image_generator(self, image_generation_engine):
        return ImageGenerator(image_generation_engine=image_generation_engine)

    def test_validate_output_configs(self, image_generation_engine):
        with pytest.raises(ValueError):
            ImageGenerator(image_generation_engine=image_generation_engine, output_dir="test", output_file="test")

    def test_text_to_image(self, image_generator):
        image_generator.image_generation_engine.text_to_image.return_value = Mock(
            value=b"image data", mime_type="image/png", width=512, height=512, model="test model", prompt="test prompt"
        )

        image_artifact = image_generator.generate_image_from_text(
            params={"values": {"prompts": ["test prompt"], "negative_prompts": ["test negative prompt"]}}
        )

        assert image_artifact

    def test_text_to_image_with_outfile(self, image_generation_engine):
        outfile = f"{tempfile.gettempdir()}/{str(uuid.uuid4())}.png"
        image_generator = ImageGenerator(image_generation_engine=image_generation_engine, output_file=outfile)

        image_generator.image_generation_engine.text_to_image.return_value = Mock(
            value=b"image data", mime_type="image/png", width=512, height=512, model="test model", prompt="test prompt"
        )

        image_artifact = image_generator.generate_image_from_text(
            params={"values": {"prompts": ["test prompt"], "negative_prompts": ["test negative prompt"]}}
        )

        assert image_artifact
        assert os.path.exists(outfile)

    def test_text_to_image_returns_error_artifact_on_exception(self, image_generator):
        image_generator.image_generation_engine.text_to_image.side_effect = Exception("test exception")

        error_artifact = image_generator.generate_image_from_text(
            params={"values": {"prompts": ["test prompt"], "negative_prompts": ["test negative prompt"]}}
        )

        assert error_artifact
        assert error_artifact.value == "test exception"
