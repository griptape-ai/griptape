import pytest

from griptape.loaders.file_loader import FileLoader


class TestFileLoader:
    @pytest.fixture()
    def loader(self):
        return FileLoader()

    @pytest.fixture(params=["path_from_resource_path"])
    def create_source(self, request):
        return request.getfixturevalue(request.param)

    def test_load_pdf(self, loader, create_source):
        artifact = loader.load(create_source("bitcoin.pdf"))

        assert len(artifact) == 9
        assert artifact[0].value.startswith("Bitcoin: A Peer-to-Peer")
        assert artifact[-1].value.endswith('its applications," 1957.\n9')

    def test_load_txt(self, loader, create_source):
        artifact = loader.load(create_source("test.txt"))

        assert artifact.value.startswith("foobar foobar foobar")
        assert artifact.encoding == loader.encoding

    def test_load_csv(self, loader, create_source):
        artifact = loader.load(create_source("test-1.csv"))

        assert len(artifact) == 10
        first_artifact = artifact[0]
        assert first_artifact.value == "Foo: foo1\nBar: bar1"

    def test_load_image(self, loader, create_source):
        artifact = loader.load(create_source("small.png"))

        assert artifact.height == 32
        assert artifact.width == 32
        assert artifact.mime_type == "image/png"
        assert len(artifact.value) > 0

    def test_load_audio(self, loader, create_source):
        artifact = loader.load(create_source("sentences.wav"))

        assert artifact.mime_type == "audio/x-wav"
        assert len(artifact.value) > 0
