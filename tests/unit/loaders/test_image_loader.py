import os

import pytest

from griptape.artifacts import ImageArtifact
from griptape.loaders import ImageLoader


class TestImageLoader:
    @pytest.fixture
    def loader(self):
        return ImageLoader()

    def test_init(self, loader):
        assert loader

    def test_load_with_path(self, loader):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../resources/small.png")

        artifact = loader.load(path)

        assert isinstance(artifact, ImageArtifact)
        assert artifact.name == "small.png"
        assert artifact.dir_name.endswith("/resources")
        assert artifact.height == 32
        assert artifact.width == 32
        assert artifact.mime_type == "image/png"
        assert len(artifact.value) > 0

    def test_load_jpg(self, loader):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../resources/small.jpg")

        artifact = loader.load(path)

        assert isinstance(artifact, ImageArtifact)
        assert artifact.name == "small.jpg"
        assert artifact.dir_name.endswith("/resources")
        assert artifact.height == 32
        assert artifact.width == 32
        assert artifact.mime_type == "image/png"
        assert len(artifact.value) > 0

    def test_load_webp(self, loader):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../resources/small.webp")

        artifact = loader.load(path)

        assert isinstance(artifact, ImageArtifact)
        assert artifact.name == "small.webp"
        assert artifact.dir_name.endswith("/resources")
        assert artifact.height == 32
        assert artifact.width == 32
        assert artifact.mime_type == "image/png"
        assert len(artifact.value) > 0

    def test_load_bmp(self, loader):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../resources/small.bmp")

        artifact = loader.load(path)

        assert isinstance(artifact, ImageArtifact)
        assert artifact.name == "small.bmp"
        assert artifact.dir_name.endswith("/resources")
        assert artifact.height == 32
        assert artifact.width == 32
        assert artifact.mime_type == "image/png"
        assert len(artifact.value) > 0

    def test_load_gif(self, loader):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../resources/small.gif")

        artifact = loader.load(path)

        assert isinstance(artifact, ImageArtifact)
        assert artifact.name == "small.gif"
        assert artifact.dir_name.endswith("/resources")
        assert artifact.height == 32
        assert artifact.width == 32
        assert artifact.mime_type == "image/png"
        assert len(artifact.value) > 0

    def test_load_tiff(self, loader):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../resources/small.tiff")

        artifact = loader.load(path)

        assert isinstance(artifact, ImageArtifact)
        assert artifact.name == "small.tiff"
        assert artifact.dir_name.endswith("/resources")
        assert artifact.height == 32
        assert artifact.width == 32
        assert artifact.mime_type == "image/png"
        assert len(artifact.value) > 0
