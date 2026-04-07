import tempfile

import pytest

from griptape.loaders.text_loader import TextLoader


class TestBaseFileLoader:
    @pytest.fixture(params=["ascii", "utf-8", None])
    def loader(self, request):
        encoding = request.param
        if encoding is None:
            return TextLoader()
        return TextLoader(encoding=encoding)

    @pytest.fixture(params=["path_from_resource_path"])
    def create_source(self, request):
        return request.getfixturevalue(request.param)

    def test_fetch(self, loader, create_source):
        source = create_source("test.txt")

        data = loader.fetch(source)

        assert data.startswith(b"foobar foobar foobar")

    def test_save(self, loader, create_source):
        source = create_source("test.txt")

        data = loader.load(source)

        with tempfile.TemporaryDirectory() as temp_dir:
            destination = create_source(f"{temp_dir}/test.txt")

            loader.save(destination, data)

            data_copy = loader.load(destination)

            assert data.value == data_copy.value
