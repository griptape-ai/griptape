import os
import pytest
from pypdf import PdfReader
from griptape.chunkers import PdfChunker

MAX_TOKENS = 500


class TestPdfChunker:
    @pytest.fixture
    def chunker(self):
        return PdfChunker(max_tokens=MAX_TOKENS)

    def test_chunk(self, chunker):
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../resources/bitcoin.pdf")

        reader = PdfReader(path)
        text = "".join([p.extract_text() for p in reader.pages])
        chunks = chunker.chunk(text)

        assert len(chunks) == 16

        for chunk in chunks:
            assert chunker.tokenizer.count_tokens(chunk.value) <= MAX_TOKENS

        assert chunks[0].value.startswith("Bitcoin: A Peer-to-Peer")
