import pytest

from griptape.artifacts import BlobArtifact, TextArtifact
from griptape.memory.task.storage import BlobArtifactStorage


class TestBlobArtifactStorage:
    @pytest.fixture()
    def storage(self):
        return BlobArtifactStorage()

    def test_store_artifact(self, storage):
        artifact = BlobArtifact(b"foo", name="foo")
        storage.store_artifact("test", artifact)

        assert storage.load_artifacts("test").value == [artifact]

    def test_load_artifacts(self, storage):
        artifact = BlobArtifact(b"foo", name="foo")
        storage.store_artifact("test", artifact)

        assert storage.load_artifacts("test").value == [artifact]
        assert not bool(storage.load_artifacts("empty"))

    def test_can_store(self, storage):
        assert not storage.can_store(TextArtifact("foo"))
        assert storage.can_store(BlobArtifact(b"foo"))

    def test_summarize(self, storage):
        storage.store_artifact("foo", BlobArtifact(b"test"))

        assert storage.summarize("foo").value == "can't summarize artifacts"

    def test_query(self, storage):
        storage.store_artifact("foo", BlobArtifact(b"test"))

        assert storage.query("foo", "query").value == "can't query artifacts"
