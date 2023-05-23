from griptape.chunkers import BaseChunker


class TextChunker(BaseChunker):
    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", "! ", "? ", " "]
