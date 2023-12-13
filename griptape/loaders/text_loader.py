from __future__ import annotations
from pathlib import Path
from typing import Optional
from attr import field, define, Factory
from griptape import utils
from griptape.artifacts import TextArtifact
from griptape.chunkers import TextChunker
from griptape.drivers import BaseEmbeddingDriver
from griptape.loaders import BaseLoader
from griptape.tokenizers import OpenAiTokenizer


@define
class TextLoader(BaseLoader):
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
    embedding_driver: BaseEmbeddingDriver | None = field(default=None, kw_only=True)
    encoding: str = field(default="utf-8", kw_only=True)

    def load(self, text: str | Path) -> list[TextArtifact]:
        return self.text_to_artifacts(text)

    def load_collection(self, texts: list[str | Path]) -> dict[str, list[TextArtifact]]:
        return utils.execute_futures_dict(
            {utils.str_to_hash(str(text)): self.futures_executor.submit(self.text_to_artifacts, text) for text in texts}
        )

    def text_to_artifacts(self, text: str | Path) -> list[TextArtifact]:
        artifacts = []

        if isinstance(text, Path):
            with open(text, encoding=self.encoding) as file:
                body = file.read()
        else:
            body = text

        if self.chunker:
            chunks = self.chunker.chunk(body)
        else:
            chunks = [TextArtifact(body)]

        if self.embedding_driver:
            for chunk in chunks:
                chunk.generate_embedding(self.embedding_driver)

        for chunk in chunks:
            chunk.encoding = self.encoding
            artifacts.append(chunk)

        return artifacts
