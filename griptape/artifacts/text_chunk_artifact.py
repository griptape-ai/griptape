from __future__ import annotations

from typing import TYPE_CHECKING

from attr import define, field

from griptape.artifacts import BaseArtifact, BaseChunkArtifact

if TYPE_CHECKING:
    from griptape.tokenizers import BaseTokenizer


@define
class TextChunkArtifact(BaseChunkArtifact):
    value: str = field(converter=str, metadata={"serializable": True})

    def __add__(self, other: BaseArtifact) -> TextChunkArtifact:
        return TextChunkArtifact(self.value + other.value)

    def __bool__(self) -> bool:
        return bool(self.value.strip())

    def token_count(self, tokenizer: BaseTokenizer) -> int:
        return tokenizer.count_tokens(str(self.value))
