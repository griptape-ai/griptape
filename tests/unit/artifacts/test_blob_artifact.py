import base64
from griptape.artifacts import BlobArtifact, BaseArtifact
from griptape.schemas import BlobArtifactSchema


class TestBlobArtifact:
    def test_to_text(self):
        assert BlobArtifact("foobar.txt", value=b"foobar").to_text() == "foobar.txt"

    def test_serialization(self):
        artifact = BlobArtifact("foobar.txt", value=b"foobar")
        artifact_dict = BlobArtifactSchema().dump(artifact)

        assert artifact_dict["name"] == "foobar.txt"
        assert base64.b64decode(artifact_dict["value"]) == b"foobar"

    def test_deserialization(self):
        artifact = BlobArtifact("foobar.txt", value=b"foobar")
        artifact_dict = BlobArtifactSchema().dump(artifact)
        deserialized_artifact: BlobArtifact = BaseArtifact.from_dict(artifact_dict)

        assert deserialized_artifact.name == "foobar.txt"
        assert deserialized_artifact.value == b"foobar"
