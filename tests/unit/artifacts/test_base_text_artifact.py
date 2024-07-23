import pytest

from griptape.artifacts import TextArtifact
from griptape.tokenizers import OpenAiTokenizer
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestBaseTextArtifact:
    def test_generate_embedding(self):
        assert TextArtifact("foobar").generate_embedding(MockEmbeddingDriver()) == [0, 1]

    def test_embedding(self):
        artifact = TextArtifact("foobar")

        assert artifact.embedding is None
        assert artifact.generate_embedding(MockEmbeddingDriver()) == [0, 1]
        assert artifact.embedding == [0, 1]

    def test_to_bytes_encoding(self):
        assert (
            TextArtifact("ß", name="foobar.txt", encoding="ascii", encoding_error_handler="backslashreplace").to_bytes()
            == b"\\xdf"
        )

    def test_to_bytes_encoding_error(self):
        with pytest.raises(ValueError):
            assert TextArtifact("ß", encoding="ascii").to_bytes()

    def test_token_count(self):
        assert (
            TextArtifact("foobarbaz").token_count(
                OpenAiTokenizer(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)
            )
            == 2
        )
