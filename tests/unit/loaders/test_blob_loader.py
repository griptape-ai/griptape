import pytest

from griptape.artifacts import BlobArtifact
from griptape.loaders import BlobLoader


class TestTextLoader:
    @pytest.fixture(params=["utf-8", "ascii", None])
    def loader(self, request):
        encoding = request.param
        kwargs = {"encoding": encoding} if encoding is not None else {}
        return BlobLoader(**kwargs)

    @pytest.fixture(params=["path_from_resource_path"])
    def create_source(self, request):
        return request.getfixturevalue(request.param)

    def test_load(self, loader, create_source):
        source = create_source("test.txt")

        artifact = loader.load(source)

        assert isinstance(artifact, BlobArtifact)
        if loader.encoding is None:
            assert artifact.value.decode("utf-8").startswith("foobar foobar foobar")
        else:
            assert artifact.encoding == loader.encoding
            assert artifact.to_text().startswith("foobar foobar foobar")

    def test_load_collection(self, loader, create_source):
        resource_paths = ["test.txt"]
        sources = [create_source(resource_path) for resource_path in resource_paths]

        collection = loader.load_collection(sources)

        keys = {loader.to_key(source) for source in sources}
        assert collection.keys() == keys

        key = next(iter(keys))
        artifact = collection[key]

        assert isinstance(artifact, BlobArtifact)
        if loader.encoding is None:
            assert artifact.value.decode("utf-8").startswith("foobar foobar foobar")
        else:
            assert artifact.encoding == loader.encoding
            assert artifact.to_text().startswith("foobar foobar foobar")
