from unittest.mock import Mock

import pytest

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.drivers.embedding.twelvelabs import TwelveLabsEmbeddingDriver


class TestTwelveLabsEmbeddingDriver:
    @pytest.fixture(autouse=True)
    def mock_client(self, mocker):
        mock_client = mocker.patch("twelvelabs.TwelveLabs")
        mock_client.return_value.embed.create.return_value = Mock(
            text_embedding=Mock(segments=[Mock(float_=[0, 1, 0])]),
            image_embedding=Mock(segments=[Mock(float_=[1, 0, 1])]),
        )
        return mock_client

    def test_init(self):
        assert TwelveLabsEmbeddingDriver()

    def test_embed_string(self):
        assert TwelveLabsEmbeddingDriver().embed("foobar") == [0, 1, 0]

    def test_embed_text_artifact(self):
        assert TwelveLabsEmbeddingDriver().embed(TextArtifact("foobar")) == [0, 1, 0]

    def test_embed_image_artifact(self):
        artifact = ImageArtifact(b"foobar", format="jpeg", width=1, height=1)
        assert TwelveLabsEmbeddingDriver().embed(artifact) == [1, 0, 1]

    def test_embed_no_segments_raises(self, mock_client):
        mock_client.return_value.embed.create.return_value = Mock(text_embedding=Mock(segments=[]))
        with pytest.raises(ValueError, match="no embedding segments"):
            TwelveLabsEmbeddingDriver().embed("foobar")
