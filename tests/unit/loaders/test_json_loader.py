import pytest

from griptape.loaders import JsonLoader


class TestJsonLoader:
    @pytest.fixture(params=["ascii", "utf-8", None])
    def loader(self, request):
        encoding = request.param
        if encoding is None:
            return JsonLoader()
        return JsonLoader(encoding=encoding)

    @pytest.fixture(params=["path_from_resource_path"])
    def create_source(self, request):
        return request.getfixturevalue(request.param)

    def test_load(self, loader, create_source):
        source = create_source("test.json")

        artifact = loader.load(source)

        assert artifact.value["name"] == "John Doe"
        assert artifact.encoding == loader.encoding

    def test_load_collection(self, loader, create_source):
        resource_paths = ["test.json"]
        sources = [create_source(resource_path) for resource_path in resource_paths]

        collection = loader.load_collection(sources)

        keys = {loader.to_key(source) for source in sources}
        assert collection.keys() == keys

        key = next(iter(keys))
        artifact = collection[key]

        assert artifact.encoding == loader.encoding
