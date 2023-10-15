import pytest
from griptape.artifacts import BlobArtifact, TextArtifact
from griptape.memory.tool.storage import BlobToolMemoryStorage


class TestBlobToolMemoryStorage:
    @pytest.fixture
    def storage(self):
        return BlobToolMemoryStorage()

    def test_store_artifact(self, storage):
        artifact = BlobArtifact(b"foo", name="foo")
        storage.store_artifact("test", artifact)

        assert storage.load_artifacts("test").value == [artifact]

    def test_load_artifacts(self, storage):
        artifact = BlobArtifact(b"foo", name="foo")
        storage.store_artifact("test", artifact)

        assert storage.load_artifacts("test").value == [artifact]
        assert storage.load_artifacts("empty").is_empty()

    def test_can_store(self, storage):
        assert not storage.can_store(TextArtifact("foo"))
        assert storage.can_store(BlobArtifact(b"foo"))

    def test_summarize(self, storage):
        storage.store_artifact("foo", BlobArtifact(b"test"))

        assert storage.summarize("foo").value == "Can't summarize artifacts"
