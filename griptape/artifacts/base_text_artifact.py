from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape.artifacts import BaseArtifact

if TYPE_CHECKING:
    from griptape.drivers import BaseEmbeddingDriver
    from griptape.tokenizers import BaseTokenizer


@define
class BaseTextArtifact(BaseArtifact):
    encoding: str = field(default="utf-8", kw_only=True)
    encoding_error_handler: str = field(default="strict", kw_only=True)
    _embedding: list[float] = field(factory=list, kw_only=True)

    @property
    def embedding(self) -> Optional[list[float]]:
        return None if len(self._embedding) == 0 else self._embedding

    def generate_embedding(self, driver: BaseEmbeddingDriver) -> Optional[list[float]]:
        self._embedding.clear()
        self._embedding.extend(driver.embed_string(str(self.value)))

        return self.embedding

    def token_count(self, tokenizer: BaseTokenizer) -> int:
        return tokenizer.count_tokens(str(self.value))

    def to_bytes(self) -> bytes:
        return str(self.value).encode(encoding=self.encoding, errors=self.encoding_error_handler)
