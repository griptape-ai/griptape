import pytest
from griptape.chunkers import TextChunker
from griptape.tokenizers import BaseTokenizer

MAX_TOKENS = 50


def gen_paragraph(max_tokens: int, tokenizer: BaseTokenizer, sentence_separator: str) -> str:
    all_text = ""
    word = "foo"
    index = 0
    add_word = lambda base, w, i: sentence_separator.join([base, f"{w}-{i}"])

    while max_tokens >= tokenizer.token_count(add_word(all_text, word, index)):
        all_text = f"{word}-{index}" if all_text == "" else add_word(all_text, word, index)
        index += 1

    return all_text + sentence_separator


class TestTextChunker:    
    @pytest.fixture
    def chunker(self):        
        return TextChunker(
            max_tokens_per_chunk=MAX_TOKENS
        )
    
    def test_small_chunks(self, chunker):
        text = [
            gen_paragraph(MAX_TOKENS, chunker.tokenizer, "? "),
            "\n\n",
            gen_paragraph(MAX_TOKENS, chunker.tokenizer, ". ")
        ]
        chunks = chunker.chunk("".join(text))

        assert len(chunks) == 2

        for chunk in chunks:
            assert chunker.tokenizer.token_count(chunk) <= MAX_TOKENS

        assert chunks[0].startswith("foo-0?")
        assert chunks[1].startswith("foo-0.")

        assert chunks[0].endswith("? foo-11?")
        assert chunks[1].endswith(". foo-11.")

    def test_large_chunks(self, chunker):
        text = [
            gen_paragraph(MAX_TOKENS * 2, chunker.tokenizer, "! "),
            "\n\n",
            gen_paragraph(MAX_TOKENS, chunker.tokenizer, ". ")
        ]
        chunks = chunker.chunk("".join(text))

        assert len(chunks) == 4

        for chunk in chunks:
            assert chunker.tokenizer.token_count(chunk) <= MAX_TOKENS

        assert chunks[0].startswith("foo-0!")
        assert chunks[1].startswith("foo-10!")
        assert chunks[2].startswith("foo-16!")
        assert chunks[3].startswith("foo-0.")

        assert chunks[0].endswith("! foo-9!")
        assert chunks[1].endswith("! foo-15!")
        assert chunks[2].endswith("! foo-24!")
        assert chunks[3].endswith(". foo-11.")

    def test_separators(self, chunker):
        text = [
            gen_paragraph(MAX_TOKENS * 2, chunker.tokenizer, "! "),
            "\n\n",
            gen_paragraph(MAX_TOKENS, chunker.tokenizer, ". "),
            "\n",
            gen_paragraph(MAX_TOKENS + 1, chunker.tokenizer, "? "),
            "\n\n",
            gen_paragraph(MAX_TOKENS + 1, chunker.tokenizer, " ")
        ]
        chunks = chunker.chunk("".join(text))

        assert len(chunks) == 8

        for chunk in chunks:
            assert chunker.tokenizer.token_count(chunk) <= MAX_TOKENS

        assert chunks[0].startswith("foo-0!")
        assert chunks[1].startswith("foo-10!")
        assert chunks[2].startswith("foo-16!")
        assert chunks[3].startswith("foo-0.")
        assert chunks[4].startswith("foo-0?")
        assert chunks[5].startswith("foo-5?")
        assert chunks[6].startswith("foo-0")
        assert chunks[7].startswith("foo-6")

        assert chunks[0].endswith("! foo-9!")
        assert chunks[1].endswith("! foo-15!")
        assert chunks[2].endswith("! foo-24!")
        assert chunks[3].endswith(". foo-11.")
        assert chunks[4].endswith("? foo-4?")
        assert chunks[5].endswith("? foo-12?")
        assert chunks[6].endswith(" foo-5")
        assert chunks[7].endswith(" foo-16")
