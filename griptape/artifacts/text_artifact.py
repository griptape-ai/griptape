from __future__ import annotations
from typing import TYPE_CHECKING
from attr import define, field
from griptape.artifacts import BaseArtifact

if TYPE_CHECKING:
    from griptape.drivers import BaseEmbeddingDriver
    from griptape.tokenizers import BaseTokenizer


@define(frozen=True)
class TextArtifact(BaseArtifact):
    value: str = field()
    __embedding: list[float] = field(factory=list)

    def embedding(self, driver: BaseEmbeddingDriver) -> list[float]:
        if len(self.__embedding) == 0:
            self.__embedding.extend(driver.embed_string(self.value))

        return self.__embedding

    def token_count(self, tokenizer: BaseTokenizer) -> int:
        return tokenizer.token_count(self.value)

    def to_text(self) -> str:
        return self.value

    def to_dict(self) -> dict:
        from griptape.schemas import TextArtifactSchema

        return dict(TextArtifactSchema().dump(self))
