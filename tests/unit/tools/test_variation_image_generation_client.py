import os
import tempfile
import uuid
from unittest.mock import Mock

import pytest

from griptape.artifacts import ImageArtifact
from griptape.tools import VariationImageGenerationClient


class TestVariationImageGenerationClient:
    @pytest.fixture()
    def image_artifact(self) -> ImageArtifact:
        return ImageArtifact(value=b"image_data", format="png", width=512, height=512, name="name")

    @pytest.fixture()
    def image_generation_engine(self) -> Mock:
        return Mock()

    @pytest.fixture()
    def image_loader(self) -> Mock:
        loader = Mock()
        loader.load.return_value = ImageArtifact(value=b"image_data", format="png", width=512, height=512)

        return loader

    @pytest.fixture()
    def image_generator(self, image_generation_engine, image_loader) -> VariationImageGenerationClient:
        return VariationImageGenerationClient(engine=image_generation_engine, image_loader=image_loader)

    def test_validate_output_configs(self, image_generation_engine, image_loader) -> None:
        with pytest.raises(ValueError):
            VariationImageGenerationClient(
                engine=image_generation_engine, output_dir="test", output_file="test", image_loader=image_loader
            )

    def test_image_variation(self, image_generator, path_from_resource_path) -> None:
        image_generator.engine.run.return_value = Mock(
            value=b"image data", format="png", width=512, height=512, model="test model", prompt="test prompt"
        )

        image_artifact = image_generator.image_variation_from_file(
            params={
                "values": {
                    "prompt": "test prompt",
                    "negative_prompt": "test negative prompt",
                    "image_file": path_from_resource_path("small.png"),
                }
            }
        )

        assert image_artifact

    def test_image_variation_with_outfile(self, image_generation_engine, image_loader, path_from_resource_path) -> None:
        outfile = f"{tempfile.gettempdir()}/{str(uuid.uuid4())}.png"
        image_generator = VariationImageGenerationClient(
            engine=image_generation_engine, output_file=outfile, image_loader=image_loader
        )

        image_generator.engine.run.return_value = Mock(  # pyright: ignore[reportFunctionMemberAccess]
            value=b"image data", format="png", width=512, height=512, model="test model", prompt="test prompt"
        )

        image_artifact = image_generator.image_variation_from_file(
            params={
                "values": {
                    "prompt": "test prompt",
                    "negative_prompt": "test negative prompt",
                    "image_file": path_from_resource_path("small.png"),
                }
            }
        )

        assert image_artifact
        assert os.path.exists(outfile)

    def test_image_variation_from_memory(self, image_generation_engine, image_artifact):
        image_generator = VariationImageGenerationClient(engine=image_generation_engine)
        memory = Mock()
        memory.load_artifacts = Mock(return_value=[image_artifact])
        image_generator.find_input_memory = Mock(return_value=memory)

        image_generator.engine.run.return_value = Mock(  # pyright: ignore[reportFunctionMemberAccess]
            value=b"image data", format="png", width=512, height=512, model="test model", prompt="test prompt"
        )

        image_artifact = image_generator.image_variation_from_memory(
            params={
                "values": {
                    "prompt": "test prompt",
                    "negative_prompt": "test negative prompt",
                    "artifact_namespace": "namespace",
                    "artifact_name": "name",
                    "memory_name": "memory",
                }
            }
        )

        assert image_artifact
