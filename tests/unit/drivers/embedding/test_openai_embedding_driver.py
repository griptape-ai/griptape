from contextlib import nullcontext
from unittest.mock import Mock

import pytest

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.drivers.embedding.openai import OpenAiEmbeddingDriver
from griptape.tokenizers import OpenAiTokenizer


class TestOpenAiEmbeddingDriver:
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
        assert OpenAiEmbeddingDriver()

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
                pytest.raises(ValueError, match="OpenAiEmbeddingDriver does not support embedding images."),
            ),
        ],
    )
    def test_embed(self, value, expected_output, expected_error):
        with expected_error:
            assert OpenAiEmbeddingDriver().embed(value) == expected_output

    @pytest.mark.parametrize("model", OpenAiTokenizer.EMBEDDING_MODELS)
    def test_try_embed_chunk_replaces_newlines_in_older_ada_models(self, model, mock_openai):
        OpenAiEmbeddingDriver(model=model).try_embed_chunk("foo\nbar")
        assert mock_openai.call_args.kwargs["input"] == "foo bar" if model.endswith("001") else "foo\nbar"
