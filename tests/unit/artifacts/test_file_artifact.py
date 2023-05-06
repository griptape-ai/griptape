import base64
from griptape.artifacts import FileArtifact, BaseArtifact
from griptape.schemas import FileArtifactSchema


class TestFileArtifact:
    def test_to_text(self):
        assert FileArtifact("foobar.txt", path="test", value=b"foobar").to_text() == "test/foobar.txt"

    def test_full_path_with_path(self):
        assert FileArtifact("foobar.txt", path="test", value=b"foobar").full_path == "test/foobar.txt"

    def test_full_path_without_path(self):
        assert FileArtifact("foobar.txt", value=b"foobar").full_path == "foobar.txt"

    def test_serialization(self):
        artifact = FileArtifact("foobar.txt", path="test", value=b"foobar")
        artifact_dict = FileArtifactSchema().dump(artifact)

        assert artifact_dict["name"] == "foobar.txt"
        assert artifact_dict["path"] == "test"
        assert base64.b64decode(artifact_dict["value"]) == b"foobar"

    def test_deserialization(self):
        artifact = FileArtifact("foobar.txt", path="test", value=b"foobar")
        artifact_dict = FileArtifactSchema().dump(artifact)
        deserialized_artifact: FileArtifact = BaseArtifact.from_dict(artifact_dict)

        assert deserialized_artifact.name == "foobar.txt"
        assert deserialized_artifact.path == "test"
        assert deserialized_artifact.value == b"foobar"
