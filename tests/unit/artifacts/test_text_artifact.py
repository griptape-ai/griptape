import json
import pytest
from griptape.artifacts import TextArtifact, BaseArtifact, TextChunkArtifact
from griptape.tokenizers import OpenAiTokenizer
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestTextArtifact:
    def test_value_type_conversion(self):
        assert TextArtifact("1").value == "1"
        assert TextArtifact(1).value == "1"

    def test___add__(self):
        assert (TextArtifact("foo") + TextArtifact("bar")).value == "foobar"

    def test_generate_embedding(self):
        assert TextArtifact("foobar").generate_embedding(MockEmbeddingDriver()) == [0, 1]

    def test_embedding(self):
        artifact = TextArtifact("foobar")

        assert artifact.embedding is None
        assert artifact.generate_embedding(MockEmbeddingDriver()) == [0, 1]
        assert artifact.embedding == [0, 1]

    def test_to_text(self):
        assert TextArtifact("foobar").to_text() == "foobar"

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

    def test_to_dict(self):
        assert TextArtifact("foobar").to_dict()["value"] == "foobar"

    def test_from_dict(self):
        assert BaseArtifact.from_dict(TextArtifact("foobar").to_dict()).value == "foobar"

    def test_to_json(self):
        assert json.loads(TextArtifact("foobar").to_json())["value"] == "foobar"

    def test_from_json(self):
        assert BaseArtifact.from_json(TextArtifact("foobar").to_json()).value == "foobar"

    def test_name(self):
        artifact = TextArtifact("foo")

        assert artifact.name == artifact.id
        assert TextArtifact("foo", name="bar").name == "bar"

    def test_from_chunks(self):
        chunks = [TextChunkArtifact("foo"), TextChunkArtifact("bar")]

        assert TextArtifact.from_chunks(chunks).value == "foobar"
