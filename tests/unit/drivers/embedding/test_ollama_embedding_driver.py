from contextlib import nullcontext

import pytest

from griptape.artifacts.image_artifact import ImageArtifact
from griptape.artifacts.text_artifact import TextArtifact
from griptape.drivers.embedding.ollama import OllamaEmbeddingDriver


class TestOllamaEmbeddingDriver:
    @pytest.fixture(autouse=True)
    def mock_client(self, mocker):
        mock_client = mocker.patch("ollama.Client")

        mock_client.return_value.embeddings.return_value = {"embedding": [0, 1, 0]}

        return mock_client

    def test_init(self):
        assert OllamaEmbeddingDriver(model="foo")

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
                pytest.raises(ValueError, match="OllamaEmbeddingDriver does not support embedding images."),
            ),
        ],
    )
    def test_embed(self, value, expected_output, expected_error):
        with expected_error:
            assert OllamaEmbeddingDriver(model="foo").embed(value) == expected_output
