from pathlib import Path
from typing import Union, IO, Optional
from attr import define
from griptape.chunkers import BaseChunker
from PyPDF2 import PdfReader


@define
class PdfChunker(BaseChunker):
    DEFAULT_SEPARATORS = ["\n\n", ". ", "! ", "? ", " "]

    def chunk(self, stream: Union[str, IO, Path], password: Optional[str] = None) -> list[str]:
        reader = PdfReader(
            stream,
            password=password
        )
        text = "".join([p.extract_text() for p in reader.pages])

        return self.chunk_recursively(text)
