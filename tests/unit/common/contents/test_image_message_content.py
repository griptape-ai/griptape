import pytest

from griptape.artifacts.image_artifact import ImageArtifact
from griptape.common import ImageMessageContent


class TestImageMessageContent:
    def test_init(self):
        assert ImageMessageContent(ImageArtifact(b"foo", format="jpg", width=100, height=100)).artifact.value == b"foo"

    def test_from_deltas(self):
        with pytest.raises(NotImplementedError):
            ImageMessageContent.from_deltas([])
