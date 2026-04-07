from contextlib import nullcontext
from unittest.mock import MagicMock

import pytest

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.drivers.embedding.google import GoogleEmbeddingDriver


class TestGoogleEmbeddingDriver:
    @pytest.fixture(autouse=True)
    def mock_genai(self, mocker):
        mock_embed_content = mocker.patch("google.generativeai.embed_content")

        mock_value = MagicMock()
        value = {"embedding": [0, 1, 0]}
        mock_value.__getitem__.side_effect = value.__getitem__
        mock_embed_content.return_value = mock_value

        return mock_embed_content

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
