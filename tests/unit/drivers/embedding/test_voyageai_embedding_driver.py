from contextlib import nullcontext
from unittest.mock import Mock

import pytest

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.drivers.embedding.voyageai import VoyageAiEmbeddingDriver


class TestVoyageAiEmbeddingDriver:
    @pytest.fixture(autouse=True)
    def mock_client(self, mocker):
        mock_client = mocker.patch("voyageai.Client")
        mock_client.return_value.embed.return_value = Mock(embeddings=[[0, 1, 0]])
        mock_client.return_value.count_tokens.return_value = 5
        mock_client.return_value.multimodal_embed.return_value = Mock(embeddings=[[0, 1, 0]])

        return mock_client

    @pytest.fixture(autouse=True)
    def mock_pil_image(self, mocker):
        mock_image = mocker.MagicMock()
        mocker.patch("PIL.Image.open", return_value=mock_image)

    def test_init(self):
        assert VoyageAiEmbeddingDriver()

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
                [0, 1, 0],
                nullcontext(),
            ),
        ],
    )
    def test_embed(self, value, expected_output, expected_error):
        with expected_error:
            assert VoyageAiEmbeddingDriver().embed(value) == expected_output
