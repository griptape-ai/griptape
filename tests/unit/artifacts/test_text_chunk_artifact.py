import json
from griptape.artifacts import BaseArtifact, TextChunkArtifact, TextArtifact
from griptape.tokenizers import OpenAiTokenizer


class TestTextChunkArtifact:
    def test_value_type_conversion(self):
        assert TextChunkArtifact("1").value == "1"
        assert TextChunkArtifact(1).value == "1"  # pyright: ignore[reportArgumentType]

    def test___add__(self):
        assert (TextChunkArtifact("foo") + TextChunkArtifact("bar")).value == "foobar"

    def test__bool__(self):
        assert TextChunkArtifact("foo")
        assert not TextChunkArtifact("")

    def test_to_text(self):
        assert TextChunkArtifact("foobar").to_text() == "foobar"

    def test_token_count(self):
        assert (
            TextChunkArtifact("foobarbaz").token_count(
                OpenAiTokenizer(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)
            )
            == 2
        )

    def test_to_dict(self):
        assert TextChunkArtifact("foobar").to_dict()["value"] == "foobar"

    def test_from_dict(self):
        assert BaseArtifact.from_dict(TextChunkArtifact("foobar").to_dict()).value == "foobar"

    def test_to_json(self):
        assert json.loads(TextChunkArtifact("foobar").to_json())["value"] == "foobar"

    def test_from_json(self):
        assert BaseArtifact.from_json(TextChunkArtifact("foobar").to_json()).value == "foobar"

    def test_name(self):
        artifact = TextChunkArtifact("foo")

        assert artifact.name == artifact.id
        assert TextChunkArtifact("foo", name="bar").name == "bar"

    def test_from_chunks(self):
        chunks = [TextChunkArtifact("foo"), TextChunkArtifact("bar")]

        assert TextArtifact.from_chunks(chunks).value == "foobar"
