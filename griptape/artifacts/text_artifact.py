from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from attr import define, field
from griptape.artifacts import BaseArtifact

if TYPE_CHECKING:
    from griptape.drivers import BaseEmbeddingDriver
    from griptape.tokenizers import BaseTokenizer


@define
class TextArtifact(BaseArtifact):
    value: str = field(converter=str)
    encoding: str = field(default="utf-8", kw_only=True)
    encoding_error_handler: str = field(default="strict", kw_only=True)
    __embedding: list[float] = field(factory=list, kw_only=True)

    @property
    def embedding(self) -> list[float] | None:
        return None if len(self.__embedding) == 0 else self.__embedding

    def __add__(self, other: TextArtifact) -> TextArtifact:
        return TextArtifact(self.value + other.value)

    def __bool__(self) -> bool:
        return bool(self.value.strip())

    def generate_embedding(self, driver: BaseEmbeddingDriver) -> list[float]:
        self.__embedding.clear()
        self.__embedding.extend(driver.embed_string(str(self.value)))

        return self.embedding

    def token_count(self, tokenizer: BaseTokenizer) -> int:
        return tokenizer.count_tokens(str(self.value))

    def to_text(self) -> str:
        return self.value

    def to_bytes(self) -> bytes:
        return self.value.encode(encoding=self.encoding, errors=self.encoding_error_handler)

    def to_dict(self) -> dict:
        from griptape.schemas import TextArtifactSchema

        return dict(TextArtifactSchema().dump(self))
