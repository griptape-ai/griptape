import os

import pytest

from griptape.artifacts import ImageArtifact
from griptape.loaders.image_loader import ImageLoader


class TestImageLoader:
    @pytest.fixture
    def loader(self):
        return ImageLoader()

    def test_init(self, loader):
        assert loader

    def test_load_with_path(self, loader):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../resources/pig-balloon.png")

        artifact = loader.load(path)

        assert isinstance(artifact, ImageArtifact)
        assert artifact.name == "pig-balloon.png"
        assert artifact.dir_name.endswith("/resources")
        assert artifact.height == 1024
        assert artifact.width == 1024
        assert artifact.mime_type == "image/png"
