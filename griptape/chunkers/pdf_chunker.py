from griptape.chunkers import BaseChunker


class PdfChunker(BaseChunker):
    DEFAULT_SEPARATORS = ["\n\n", ". ", "! ", "? ", " "]
