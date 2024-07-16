import pytest

from griptape.artifacts import BlobArtifact, TextArtifact
from tests.utils import defaults


class TestTextArtifactStorage:
    @pytest.fixture()
    def storage(self):
        return defaults.text_tool_artifact_storage()

    def test_store_artifact(self, storage):
        artifact = TextArtifact("foo", name="foo")
        storage.store_artifact("test", artifact)

        assert storage.load_artifacts("test").value[0].value == "foo"

    def test_load_artifacts(self, storage):
        artifact = TextArtifact("foo", name="foo")
        storage.store_artifact("test", artifact)

        assert storage.load_artifacts("test").value[0].value == "foo"
        assert not bool(storage.load_artifacts("empty"))

    def test_can_store(self, storage):
        assert storage.can_store(TextArtifact("foo"))
        assert not storage.can_store(BlobArtifact(b"foo"))

    def test_summarize(self, storage):
        storage.store_artifact("foo", TextArtifact("test"))

        assert storage.summarize("foo").value == "mock output"

    def test_query(self, storage):
        storage.store_artifact("foo", TextArtifact("test"))

        assert storage.query("foo", "query").value == "mock output"
