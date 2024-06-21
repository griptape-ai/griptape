from griptape.artifacts import TextArtifact
from griptape.drivers import BaseVectorStoreDriver


class TestEntry:
    def test_from_dict(self):
        entry_dict = {"id": "test", "vector": [], "meta": {"artifact": TextArtifact("foo").to_json()}}
        assert BaseVectorStoreDriver.Entry.from_dict(entry_dict).id == "test"

    def test_to_artifact(self):
        entry = BaseVectorStoreDriver.Entry(id="test", vector=[], meta={"artifact": TextArtifact("foo").to_json()})
        assert entry.to_artifact().value == "foo"
