from __future__ import annotations
from abc import ABC, abstractmethod
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.chunkers import ChunkSeparator
from griptape.tokenizers import BaseTokenizer, OpenAiTokenizer


@define
class BaseChunker(ABC):
    DEFAULT_SEPARATORS = [ChunkSeparator(" ")]

    separators: list[ChunkSeparator] = field(
        default=Factory(lambda self: self.DEFAULT_SEPARATORS, takes_self=True), kw_only=True
    )
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda: OpenAiTokenizer(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)), kw_only=True
    )
    max_tokens: int = field(
        default=Factory(lambda self: self.tokenizer.max_input_tokens, takes_self=True), kw_only=True
    )

    def chunk(self, text: TextArtifact | str) -> list[TextArtifact]:
        return self.try_chunk(text)

    @abstractmethod
    def try_chunk(self, text: TextArtifact | str) -> list[TextArtifact]:
        ...
