import pytest

from griptape.artifacts import BaseArtifact, GenericArtifact


class TestGenericArtifact:
    @pytest.fixture()
    def generic_artifact(self):
        return GenericArtifact(
            value="some generic data",
        )

    def test_to_text(self, generic_artifact: GenericArtifact):
        assert generic_artifact.to_text() == "some generic data"

    def test_to_dict(self, generic_artifact: GenericArtifact):
        generic_dict = generic_artifact.to_dict()

        assert generic_dict["value"] == "some generic data"

    def test_deserialization(self, generic_artifact):
        artifact_dict = generic_artifact.to_dict()
        deserialized_artifact = BaseArtifact.from_dict(artifact_dict)

        assert isinstance(deserialized_artifact, GenericArtifact)

        assert deserialized_artifact.value == "some generic data"
