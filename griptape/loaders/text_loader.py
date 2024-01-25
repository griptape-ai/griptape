from __future__ import annotations

from typing import Optional

from attr import field, define, Factory
from pathlib import Path

from griptape import utils
from griptape.artifacts import TextArtifact
from griptape.chunkers import TextChunker
from griptape.drivers import BaseEmbeddingDriver
from griptape.loaders import BaseTextLoader
from griptape.tokenizers import OpenAiTokenizer


@define
class TextLoader(BaseTextLoader):
    MAX_TOKEN_RATIO = 0.5

    tokenizer: OpenAiTokenizer = field(
        default=Factory(lambda: OpenAiTokenizer(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)), kw_only=True
    )
    max_tokens: int = field(
        default=Factory(lambda self: round(self.tokenizer.max_tokens * self.MAX_TOKEN_RATIO), takes_self=True),
        kw_only=True,
    )
    chunker: TextChunker = field(
        default=Factory(
            lambda self: TextChunker(tokenizer=self.tokenizer, max_tokens=self.max_tokens), takes_self=True
        ),
        kw_only=True,
    )
    embedding_driver: Optional[BaseEmbeddingDriver] = field(default=None, kw_only=True)
    encoding: str = field(default="utf-8", kw_only=True)

    def load(self, source: str | Path, *args, **kwargs) -> list[TextArtifact]:
        return self._text_to_artifacts(source)

    def load_collection(self, sources: list[str | Path], *args, **kwargs) -> dict[str, list[TextArtifact]]:
        return utils.execute_futures_dict(
            {
                utils.str_to_hash(str(source)): self.futures_executor.submit(self._text_to_artifacts, source)
                for source in sources
            }
        )
