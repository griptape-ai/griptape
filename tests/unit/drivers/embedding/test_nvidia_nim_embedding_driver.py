from contextlib import nullcontext
from unittest.mock import Mock

import pytest

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.drivers.embedding.nvidia_nim import NvidiaNimEmbeddingDriver


class TestNvidiaNimEmbeddingDriver:
    @pytest.fixture(autouse=True)
    def mock_openai(self, mocker):
        mock_chat_create = mocker.patch("openai.OpenAI").return_value.embeddings.create

        mock_embedding = Mock()
        mock_embedding.embedding = [0, 1, 0]
        mock_response = Mock()
        mock_response.data = [mock_embedding]

        mock_chat_create.return_value = mock_response

        return mock_chat_create

    def test_init(self):
        assert NvidiaNimEmbeddingDriver()

    @pytest.mark.parametrize(
        ("value", "vector_operation", "expected_output", "expected_error"),
        [
            ("foobar", "query", [0, 1, 0], nullcontext()),
            (
                TextArtifact("foobar"),
                "query",
                [0, 1, 0],
                nullcontext(),
            ),
            (
                ImageArtifact(b"foobar", format="jpeg", width=1, height=1),
                "query",
                [],
                pytest.raises(ValueError, match="NvidiaNimEmbeddingDriver does not support embedding images."),
            ),
            (
                "foobar",
                "invalid_operation",
                [],
                pytest.raises(ValueError, match="invalid value for vector_operation, must be one of"),
            ),
        ],
    )
    def test_embed_error(self, value, vector_operation, expected_output, expected_error):
        with expected_error:
            assert NvidiaNimEmbeddingDriver().embed(value, vector_operation=vector_operation) == expected_output

    def test_embed(self, mock_openai):
        driver = NvidiaNimEmbeddingDriver()
        driver.embed("foobar", vector_operation="query")
        assert mock_openai.call_args.kwargs["input"] == "foobar"
        assert mock_openai.call_args.kwargs["extra_body"]["input_type"] == "query"

        driver.embed("foobar", vector_operation="upsert")
        assert mock_openai.call_args.kwargs["input"] == "foobar"
        assert mock_openai.call_args.kwargs["extra_body"]["input_type"] == "passage"
