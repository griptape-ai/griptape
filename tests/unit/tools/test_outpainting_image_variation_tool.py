import os
import tempfile
import uuid
from unittest.mock import Mock

import pytest

from griptape.artifacts import ImageArtifact
from griptape.tools import OutpaintingImageGenerationTool


class TestOutpaintingImageGenerationTool:
    @pytest.fixture()
    def image_artifact(self) -> ImageArtifact:
        return ImageArtifact(value=b"image_data", format="png", width=512, height=512, name="name")

    @pytest.fixture()
    def image_generation_driver(self) -> Mock:
        return Mock()

    @pytest.fixture()
    def image_loader(self, image_artifact) -> Mock:
        loader = Mock()
        loader.load.return_value = image_artifact

        return loader

    @pytest.fixture()
    def image_generator(self, image_generation_driver, image_loader) -> OutpaintingImageGenerationTool:
        return OutpaintingImageGenerationTool(
            image_generation_driver=image_generation_driver, image_loader=image_loader
        )

    def test_validate_output_configs(self, image_generation_driver) -> None:
        with pytest.raises(ValueError):
            OutpaintingImageGenerationTool(
                image_generation_driver=image_generation_driver, output_dir="test", output_file="test"
            )

    def test_image_outpainting(self, image_generator, path_from_resource_path) -> None:
        image_generator.image_generation_driver.run_image_variation.return_value = ImageArtifact(
            value=b"image data", format="png", width=512, height=512
        )

        image_artifact = image_generator.image_outpainting_from_file(
            params={
                "values": {
                    "prompt": "test prompt",
                    "negative_prompt": "test negative prompt",
                    "image_file": path_from_resource_path("small.png"),
                    "mask_file": path_from_resource_path("small.png"),
                }
            }
        )

        assert image_artifact

    def test_image_outpainting_with_outfile(
        self, image_generation_driver, image_loader, path_from_resource_path
    ) -> None:
        outfile = f"{tempfile.gettempdir()}/{uuid.uuid4()!s}.png"
        image_generator = OutpaintingImageGenerationTool(
            image_generation_driver=image_generation_driver, output_file=outfile, image_loader=image_loader
        )

        image_generator.image_generation_driver.run_image_outpainting.return_value = ImageArtifact(  # pyright: ignore[reportFunctionMemberAccess]
            value=b"image data", format="png", width=512, height=512
        )

        image_artifact = image_generator.image_outpainting_from_file(
            params={
                "values": {
                    "prompt": "test prompt",
                    "negative_prompt": "test negative prompt",
                    "image_file": path_from_resource_path("small.png"),
                    "mask_file": path_from_resource_path("small.png"),
                }
            }
        )

        assert image_artifact
        assert os.path.exists(outfile)

    def test_image_outpainting_from_memory(self, image_generation_driver, image_artifact):
        image_generator = OutpaintingImageGenerationTool(image_generation_driver=image_generation_driver)
        memory = Mock()
        memory.load_artifacts = Mock(return_value=[image_artifact])
        image_generator.find_input_memory = Mock(return_value=memory)

        image_generator.image_generation_driver.run_image_variation.return_value = Mock(  # pyright: ignore[reportFunctionMemberAccess]
            value=b"image data", format="png", width=512, height=512, model="test model", prompt="test prompt"
        )

        image_artifact = image_generator.image_outpainting_from_memory(
            params={
                "values": {
                    "prompt": "test prompt",
                    "negative_prompt": "test negative prompt",
                    "image_artifact_namespace": "namespace",
                    "image_artifact_name": "name",
                    "mask_artifact_namespace": "namespace",
                    "mask_artifact_name": "name",
                    "memory_name": "memory",
                }
            }
        )

        assert image_artifact
