import pytest

from griptape.chunkers import MarkdownChunker
from tests.unit.chunkers.test_text_chunker import gen_paragraph

MAX_TOKENS = 50


class TestTextChunker:
    @pytest.fixture()
    def chunker(self):
        return MarkdownChunker(max_tokens=MAX_TOKENS)

    def test_chunk(self, chunker):
        text = [
            "## Header 1\n",
            gen_paragraph(MAX_TOKENS // 2, chunker.tokenizer, ". "),
            "\n## Header 2\n",
            gen_paragraph(MAX_TOKENS // 2, chunker.tokenizer, ". "),
            "\n\n",
            gen_paragraph(MAX_TOKENS // 2, chunker.tokenizer, ". "),
            "\n## Header 3\n",
            gen_paragraph(MAX_TOKENS * 2, chunker.tokenizer, ". "),
        ]
        chunks = chunker.chunk("".join(text))

        assert len(chunks) == 7

        for chunk in chunks:
            assert chunker.tokenizer.count_tokens(chunk.value) <= MAX_TOKENS

        assert chunks[0].value.startswith("## Header 1\nfoo-0")
        assert chunks[1].value.startswith("## Header 2\nfoo-0")
        assert chunks[2].value.startswith("foo-0.")
        assert chunks[3].value.startswith("## Header 3\nfoo-0")
        assert chunks[4].value.startswith("foo-5.")
        assert chunks[5].value.startswith("foo-12.")
        assert chunks[6].value.startswith("foo-19.")

        assert chunks[0].value.endswith(". foo-5.")
        assert chunks[1].value.endswith(". foo-5.")
        assert chunks[2].value.endswith(". foo-5.")
        assert chunks[3].value.endswith(". foo-4.")
        assert chunks[4].value.endswith(". foo-11.")
        assert chunks[5].value.endswith(". foo-18.")
        assert chunks[6].value.endswith(". foo-24.")
