from contextlib import nullcontext
from unittest.mock import Mock

import pytest

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.drivers.embedding.cohere import CohereEmbeddingDriver


class TestCohereEmbeddingDriver:
    @pytest.fixture(autouse=True)
    def mock_client(self, mocker):
        mock_client = mocker.patch("cohere.Client").return_value

        mock_client.embed.return_value = Mock(embeddings=[[0, 1, 0]])

        return mock_client

    def test_init(self):
        assert CohereEmbeddingDriver(model="embed-english-v3.0", api_key="bar", input_type="search_document")

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
                pytest.raises(ValueError, match="CohereEmbeddingDriver does not support embedding images."),
            ),
        ],
    )
    def test_embed(self, value, expected_output, expected_error):
        with expected_error:
            assert (
                CohereEmbeddingDriver(model="foo", api_key="bar", input_type="search_document").embed(value)
                == expected_output
            )

    def test_try_embed_chunk_extra_params(self, mock_client):
        driver = CohereEmbeddingDriver(
            model="embed-english-v3.0",
            api_key="bar",
            input_type="search_document",
            extra_params={"truncate": "END"},
        )
        driver.try_embed_chunk("foobar")

        mock_client.embed.assert_called_once_with(
            texts=["foobar"], model="embed-english-v3.0", input_type="search_document", truncate="END"
        )
