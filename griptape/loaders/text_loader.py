from __future__ import annotations

from typing import TYPE_CHECKING, Optional, cast

from attrs import Factory, define, field

from griptape.artifacts import TextArtifact
from griptape.chunkers import TextChunker
from griptape.loaders import BaseTextLoader
from griptape.tokenizers import OpenAiTokenizer

if TYPE_CHECKING:
    from griptape.drivers import BaseEmbeddingDriver


@define
class TextLoader(BaseTextLoader):
    MAX_TOKEN_RATIO = 0.5

    tokenizer: OpenAiTokenizer = field(
        default=Factory(lambda: OpenAiTokenizer(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)),
        kw_only=True,
    )
    max_tokens: int = field(
        default=Factory(lambda self: round(self.tokenizer.max_input_tokens * self.MAX_TOKEN_RATIO), takes_self=True),
        kw_only=True,
    )
    chunker: TextChunker = field(
        default=Factory(
            lambda self: TextChunker(tokenizer=self.tokenizer, max_tokens=self.max_tokens),
            takes_self=True,
        ),
        kw_only=True,
    )
    embedding_driver: Optional[BaseEmbeddingDriver] = field(default=None, kw_only=True)
    encoding: str = field(default="utf-8", kw_only=True)

    def load(self, source: bytes | str, *args, **kwargs) -> list[TextArtifact]:
        if isinstance(source, bytes):
            source = source.decode(encoding=self.encoding)
        elif isinstance(source, (bytearray, memoryview)):
            raise ValueError(f"Unsupported source type: {type(source)}")

        return self._text_to_artifacts(source)

    def load_collection(
        self,
        sources: list[bytes | str],
        *args,
        **kwargs,
    ) -> dict[str, list[TextArtifact]]:
        return cast(
            dict[str, list[TextArtifact]],
            super().load_collection(sources, *args, **kwargs),
        )
