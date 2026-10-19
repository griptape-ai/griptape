import pytest

from griptape.artifacts import VideoUrlArtifact
from griptape.common import VideoMessageContent


class TestVideoMessageContent:
    def test_init(self):
        assert VideoMessageContent(VideoUrlArtifact("https://example.com/input.mp4")).artifact.value == (
            "https://example.com/input.mp4"
        )

    def test_from_deltas(self):
        with pytest.raises(NotImplementedError):
            VideoMessageContent.from_deltas([])
