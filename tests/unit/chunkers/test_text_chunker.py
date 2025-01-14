import pytest

from griptape.artifacts import TextArtifact
from griptape.chunkers import TextChunker
from griptape.chunkers.chunk_separator import ChunkSeparator
from tests.unit.chunkers.utils import gen_paragraph

MAX_TOKENS = 50


class TestTextChunker:
    @pytest.fixture()
    def chunker(self):
        return TextChunker(max_tokens=MAX_TOKENS)

    def test_chunk_with_string(self, chunker):
        chunks = chunker.chunk(gen_paragraph(MAX_TOKENS * 2, chunker.tokenizer, " "))

        assert len(chunks) == 3

    def test_chunk_with_text_artifact(self, chunker):
        chunks = chunker.chunk(TextArtifact(gen_paragraph(MAX_TOKENS * 2, chunker.tokenizer, " ")))

        assert len(chunks) == 3

    def test_small_chunks(self, chunker):
        text = [
            gen_paragraph(MAX_TOKENS, chunker.tokenizer, "? "),
            "\n\n",
            gen_paragraph(MAX_TOKENS, chunker.tokenizer, ". "),
        ]
        chunks = chunker.chunk("".join(text))

        assert len(chunks) == 2

        for chunk in chunks:
            assert chunker.tokenizer.count_tokens(chunk.value) <= MAX_TOKENS

        assert chunks[0].value.startswith("foo-0?")
        assert chunks[1].value.startswith("foo-0.")

        assert chunks[0].value.endswith("? foo-11?")
        assert chunks[1].value.endswith(". foo-11.")

    def test_large_chunks(self, chunker):
        text = [
            gen_paragraph(MAX_TOKENS * 2, chunker.tokenizer, "! "),
            "\n\n",
            gen_paragraph(MAX_TOKENS, chunker.tokenizer, ". "),
        ]
        chunks = chunker.chunk("".join(text))

        assert len(chunks) == 4

        for chunk in chunks:
            assert chunker.tokenizer.count_tokens(chunk.value) <= MAX_TOKENS

        assert chunks[0].value.startswith("foo-0!")
        assert chunks[1].value.startswith("foo-11!")
        assert chunks[2].value.startswith("foo-17!")
        assert chunks[3].value.startswith("foo-0.")

        assert chunks[0].value.endswith("! foo-10!")
        assert chunks[1].value.endswith("! foo-16!")
        assert chunks[2].value.endswith("! foo-24!")
        assert chunks[3].value.endswith(". foo-11.")

    def test_contiguous_chunks(self, chunker):
        text = [gen_paragraph(MAX_TOKENS, chunker.tokenizer, ""), gen_paragraph(MAX_TOKENS, chunker.tokenizer, "")]
        chunks = chunker.chunk("".join(text))

        assert len(chunks) == 2

        for chunk in chunks:
            assert chunker.tokenizer.count_tokens(chunk.value) <= MAX_TOKENS

    def test_separators(self, chunker):
        text = [
            gen_paragraph(MAX_TOKENS * 2, chunker.tokenizer, "! "),
            "\n\n",
            gen_paragraph(MAX_TOKENS, chunker.tokenizer, ". "),
            "\n",
            gen_paragraph(MAX_TOKENS + 1, chunker.tokenizer, "? "),
            "\n\n",
            gen_paragraph(MAX_TOKENS + 1, chunker.tokenizer, " "),
        ]
        chunks = chunker.chunk("".join(text))

        assert len(chunks) == 8

        for chunk in chunks:
            assert chunker.tokenizer.count_tokens(chunk.value) <= MAX_TOKENS

        assert chunks[0].value.startswith("foo-0!")
        assert chunks[1].value.startswith("foo-11!")
        assert chunks[2].value.startswith("foo-17!")
        assert chunks[3].value.startswith("foo-0.")
        assert chunks[4].value.startswith("foo-0?")
        assert chunks[5].value.startswith("foo-9?")
        assert chunks[6].value.startswith("foo-0")
        assert chunks[7].value.startswith("foo-8")

        assert chunks[0].value.endswith("! foo-10!")
        assert chunks[1].value.endswith("! foo-16!")
        assert chunks[2].value.endswith("! foo-24!")
        assert chunks[3].value.endswith(". foo-11.")
        assert chunks[4].value.endswith("? foo-8?")
        assert chunks[5].value.endswith("? foo-12?")
        assert chunks[6].value.endswith(" foo-7")
        assert chunks[7].value.endswith(" foo-16")

    def test_chunk_with_max_tokens(self, chunker):
        with pytest.raises(ValueError):
            TextChunker(max_tokens=-1)

    def test_tiny_max_tokens(self, chunker):
        max_tokens = 11
        chunker.separators = [ChunkSeparator(".")]
        chunker.max_tokens = max_tokens
        text = "This is a paragraph of text. I'll count to three: one, two three."
        chunks = chunker.chunk(text)

        assert len(chunks) == 2
        for chunk in chunks:
            assert chunker.tokenizer.count_tokens(chunk.value) <= max_tokens
        assert chunks[-1].value.endswith("one, two three.")

    def test_artifact_reference(self, chunker):
        from griptape.common.reference import Reference

        reference = Reference(authors=["jason"], title="pies I like")
        chunks = chunker.chunk(TextArtifact(gen_paragraph(MAX_TOKENS * 2, chunker.tokenizer, " "), reference=reference))

        for chunk in chunks:
            assert chunk.reference == reference

        chunks = chunker.chunk(gen_paragraph(MAX_TOKENS * 2, chunker.tokenizer, " "))

        for chunk in chunks:
            assert chunk.reference is None
