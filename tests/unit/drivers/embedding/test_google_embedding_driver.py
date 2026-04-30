from contextlib import nullcontext
from unittest.mock import MagicMock

import pytest

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.drivers.embedding.google import GoogleEmbeddingDriver


class TestGoogleEmbeddingDriver:
    @pytest.fixture(autouse=True)
    def mock_client(self, mocker):
        mock_client = mocker.patch("google.genai.Client")
        mock_client.return_value.models.embed_content.return_value = MagicMock(
            embeddings=[MagicMock(values=[0, 1, 0])],
        )

        return mock_client

    def test_init(self):
        assert GoogleEmbeddingDriver()

    @pytest.mark.parametrize(
        ("value", "expected_output", "expected_error"),
        [
            ("foobar", [0, 1, 0], nullcontext()),
            (
                TextArtifact("foobar"),
                [0, 1, 0],
                nullcontext(),
            ),
            (
                ImageArtifact(b"foobar", format="jpeg", width=1, height=1),
                [],
                pytest.raises(ValueError, match="GoogleEmbeddingDriver does not support embedding images."),
            ),
        ],
    )
    def test_embed(self, value, expected_output, expected_error):
        with expected_error:
            assert GoogleEmbeddingDriver().embed(value) == expected_output
