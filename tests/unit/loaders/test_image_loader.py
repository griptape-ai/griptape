import os
from io import BytesIO

import pytest
from PIL import Image

from griptape.artifacts import ImageArtifact
from griptape.loaders import ImageLoader


class TestImageLoader:
    @pytest.fixture
    def loader(self):
        return ImageLoader()

    def test_init(self, loader):
        assert loader

    def test_load_png(self, loader):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../resources/small.png")

        with open(path, "rb") as file:
            artifact = loader.load(file.read())

        assert isinstance(artifact, ImageArtifact)
        assert artifact.name.endswith(".png")
        assert artifact.height == 32
        assert artifact.width == 32
        assert artifact.mime_type == "image/png"
        assert len(artifact.value) > 0

    def test_load_jpg(self, loader):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../resources/small.jpg")

        with open(path, "rb") as file:
            artifact = loader.load(file.read())

        assert isinstance(artifact, ImageArtifact)
        assert artifact.name.endswith(".jpeg")
        assert artifact.height == 32
        assert artifact.width == 32
        assert artifact.mime_type == "image/jpeg"
        assert len(artifact.value) > 0

    def test_load_webp(self, loader):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../resources/small.webp")

        with open(path, "rb") as file:
            artifact = loader.load(file.read())

        assert isinstance(artifact, ImageArtifact)
        assert artifact.name.endswith(".webp")
        assert artifact.height == 32
        assert artifact.width == 32
        assert artifact.mime_type == "image/webp"
        assert len(artifact.value) > 0

    def test_load_bmp(self, loader):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../resources/small.bmp")

        with open(path, "rb") as file:
            artifact = loader.load(file.read())

        assert isinstance(artifact, ImageArtifact)
        assert artifact.name.endswith(".bmp")
        assert artifact.height == 32
        assert artifact.width == 32
        assert artifact.mime_type == "image/bmp"
        assert len(artifact.value) > 0

    def test_load_gif(self, loader):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../resources/small.gif")

        with open(path, "rb") as file:
            artifact = loader.load(file.read())

        assert isinstance(artifact, ImageArtifact)
        assert artifact.name.endswith(".gif")
        assert artifact.height == 32
        assert artifact.width == 32
        assert artifact.mime_type == "image/gif"
        assert len(artifact.value) > 0

    def test_load_tiff(self, loader):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../resources/small.tiff")

        with open(path, "rb") as file:
            artifact = loader.load(file.read())

        assert isinstance(artifact, ImageArtifact)
        assert artifact.name.endswith(".tiff")
        assert artifact.height == 32
        assert artifact.width == 32
        assert artifact.mime_type == "image/tiff"
        assert len(artifact.value) > 0

    def test_normalize_format(self):
        loader = ImageLoader(format="png")
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../resources/small.jpg")

        with open(path, "rb") as file:
            artifact = loader.load(file.read())

        image = Image.open(BytesIO(artifact.value))

        assert isinstance(artifact, ImageArtifact)
        assert artifact.name.endswith(".png")
        assert artifact.height == 32
        assert artifact.width == 32
        assert artifact.mime_type == "image/png"
        assert len(artifact.value) > 0
        assert image.format == "PNG"
