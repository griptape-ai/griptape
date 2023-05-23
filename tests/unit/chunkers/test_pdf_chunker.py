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
