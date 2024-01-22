from unittest.mock import Mock

import pytest

from griptape.artifacts import ImageArtifact
from griptape.memory import TaskMemory
from griptape.utils import load_image_artifact_from_memory


class TestLoadImageArtifactFromMemory:
    @pytest.fixture
    def memory(self):
        return Mock()

    @pytest.fixture
    def image_artifact(self):
        return ImageArtifact(value=b"image data", name="image_artifact", width=512, height=512, mime_type="image/png")

    @pytest.fixture
    def mask_artifact(self):
        return ImageArtifact(value=b"mask data", name="mask_artifact", width=512, height=512, mime_type="image/png")

    def test_no_memory(self):
        with pytest.raises(ValueError):
            load_image_artifact_from_memory(None, "", "")  # pyright: ignore

    def test_no_artifacts_in_memory(self, memory):
        memory.load_artifacts.return_value = []

        with pytest.raises(ValueError) as e:
            load_image_artifact_from_memory(memory, "", "")

            assert str(e) == "no artifacts found in namespace"

    def test_no_artifacts_by_name(self, memory, image_artifact):
        memory.load_artifacts.return_value = [image_artifact]

        with pytest.raises(ValueError) as e:
            load_image_artifact_from_memory(memory, "namespace", "other_name")

            assert str(e) == "artifact name not found in namespace"

    def test_returns_one_artifact(self, memory, image_artifact):
        memory.load_artifacts.return_value = [image_artifact]

        artifact = load_image_artifact_from_memory(memory, "namespace", image_artifact.name)

        assert artifact == image_artifact

    def test_returns_multiple_artifacts(self, memory, image_artifact, mask_artifact):
        memory.load_artifacts.return_value = [mask_artifact, image_artifact, mask_artifact]

        artifact = load_image_artifact_from_memory(memory, "namespace", image_artifact.name)

        assert artifact == image_artifact
