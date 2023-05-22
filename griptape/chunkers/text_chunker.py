from attr import define
from griptape.chunkers import BaseChunker


@define
class TextChunker(BaseChunker):
    def chunk(self, text: str) -> list[str]:
        return self.chunk_recursively(text)
