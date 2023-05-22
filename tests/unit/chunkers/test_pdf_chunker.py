import os

import pytest

from griptape.chunkers import PdfChunker

MAX_TOKENS = 500


class TestPdfChunker:
    @pytest.fixture
    def chunker(self):
        return PdfChunker(
            max_tokens_per_chunk=MAX_TOKENS,
        )

    def test_chunk(self, chunker):
        path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "../.." "/resources/bitcoin.pdf"
        )

        chunks = chunker.chunk(path)

        assert len(chunks) == 16
