import pytest

from griptape.artifacts import ImageArtifact
from griptape.loaders import ImageLoader


class TestImageLoader:
    @pytest.fixture()
    def loader(self):
        return ImageLoader()

    @pytest.fixture()
    def png_loader(self):
        return ImageLoader(format="png")

    @pytest.fixture()
    def create_source(self, bytes_from_resource_path):
        return bytes_from_resource_path

    @pytest.mark.parametrize(
        ("resource_path", "mime_type"),
        [
            ("small.png", "image/png"),
            ("small.jpg", "image/jpeg"),
            ("small.webp", "image/webp"),
            ("small.bmp", "image/bmp"),
            ("small.gif", "image/gif"),
            ("small.tiff", "image/tiff"),
        ],
    )
    def test_load(self, resource_path, mime_type, loader, create_source):
        source = create_source(resource_path)

        artifact = loader.load(source)

        assert isinstance(artifact, ImageArtifact)
        assert artifact.height == 32
        assert artifact.width == 32
        assert artifact.mime_type == mime_type
        assert len(artifact.value) > 0

    @pytest.mark.parametrize(
        "resource_path", ["small.png", "small.jpg", "small.webp", "small.bmp", "small.gif", "small.tiff"]
    )
    def test_load_normalize(self, resource_path, png_loader, create_source):
        source = create_source(resource_path)

        artifact = png_loader.load(source)

        assert isinstance(artifact, ImageArtifact)
        assert artifact.height == 32
        assert artifact.width == 32
        assert artifact.mime_type == "image/png"
        assert len(artifact.value) > 0

    def test_load_collection(self, create_source, png_loader):
        resource_paths = ["small.png", "small.jpg"]
        sources = [create_source(resource_path) for resource_path in resource_paths]

        collection = png_loader.load_collection(sources)

        keys = {png_loader.to_key(source) for source in sources}

        assert collection.keys() == keys

        for key in keys:
            artifact = collection[key]
            assert isinstance(artifact, ImageArtifact)
            assert artifact.height == 32
            assert artifact.width == 32
            assert artifact.mime_type == "image/png"
            assert len(artifact.value) > 0
