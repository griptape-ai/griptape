from unittest.mock import Mock

import pytest

from griptape.artifacts import TextArtifact, ErrorArtifact, ImageArtifact
from griptape.utils import load_artifact_from_memory


class TestLoadImageArtifactFromMemory:
    @pytest.fixture
    def memory(self):
        return Mock()

    @pytest.fixture
    def text_artifact(self):
        return TextArtifact(value="text", name="text")

    @pytest.fixture
    def image_artifact(self):
        return ImageArtifact(value=b"image", name="image", mime_type="image/png", height=32, width=32)

    def test_no_memory(self):
        with pytest.raises(ValueError):
            load_artifact_from_memory(None, "", "", TextArtifact)  # pyright: ignore

    def test_no_artifacts_in_memory(self, memory):
        memory.load_artifacts.return_value = []

        with pytest.raises(ValueError) as e:
            load_artifact_from_memory(memory, "", "", TextArtifact)

            assert str(e) == "no artifacts found in namespace"

    def test_no_artifacts_by_name(self, memory, text_artifact):
        memory.load_artifacts.return_value = [text_artifact]

        with pytest.raises(ValueError) as e:
            load_artifact_from_memory(memory, "namespace", "other_name", TextArtifact)

            assert str(e) == "artifact name not found in namespace"

    def test_returns_one_artifact(self, memory, text_artifact):
        memory.load_artifacts.return_value = [text_artifact]

        artifact = load_artifact_from_memory(memory, "namespace", text_artifact.name, TextArtifact)

        assert artifact == text_artifact

    def test_returns_multiple_artifacts(self, memory, text_artifact, image_artifact):
        memory.load_artifacts.return_value = [image_artifact, text_artifact, image_artifact]

        artifact = load_artifact_from_memory(memory, "namespace", text_artifact.name, TextArtifact)

        assert artifact == text_artifact

    def test_wrong_artifact_type(self, memory, image_artifact):
        memory.load_artifacts.return_value = [image_artifact]

        with pytest.raises(ValueError) as e:
            load_artifact_from_memory(memory, "namespace", image_artifact.name, TextArtifact)

            assert str(e) == "artifact is not of type ImageArtifact"
