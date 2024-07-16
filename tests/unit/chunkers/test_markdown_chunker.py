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
            "\n" "## Header 2\n",
            gen_paragraph(MAX_TOKENS // 2, chunker.tokenizer, ". "),
            "\n\n",
            gen_paragraph(MAX_TOKENS // 2, chunker.tokenizer, ". "),
            "\n" "## Header 3\n",
            gen_paragraph(MAX_TOKENS * 2, chunker.tokenizer, ". "),
        ]
        chunks = chunker.chunk("".join(text))

        assert len(chunks) == 6

        for chunk in chunks:
            assert chunker.tokenizer.count_tokens(chunk.value) <= MAX_TOKENS

        assert chunks[0].value.startswith("## Header 1\nfoo-0")
        assert chunks[1].value.startswith("## Header 2\nfoo-0")
        assert chunks[2].value.startswith("foo-0.")
        assert chunks[3].value.startswith("## Header 3\nfoo-0")
        assert chunks[4].value.startswith("foo-9.")
        assert chunks[5].value.startswith("foo-15.")

        assert chunks[0].value.endswith(". foo-5.")
        assert chunks[1].value.endswith(". foo-5.")
        assert chunks[2].value.endswith(". foo-5.")
        assert chunks[3].value.endswith(". foo-8.")
        assert chunks[4].value.endswith(". foo-14.")
        assert chunks[5].value.endswith(". foo-24.")
