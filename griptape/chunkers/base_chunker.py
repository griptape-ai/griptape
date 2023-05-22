import re
from abc import ABC, abstractmethod

from attr import define, field, Factory
from griptape.tokenizers import TiktokenTokenizer


@define
class BaseChunker(ABC):
    SENTENCE_DELIMITERS = [". ", "! ", "? "]

    separators: list[str] = field(
        default=[
            "\n\n", "\n", "|".join(map(re.escape, SENTENCE_DELIMITERS)), " ", ""
        ],
        kw_only=True
    )
    tokenizer: TiktokenTokenizer = field(
        default=TiktokenTokenizer(),
        kw_only=True
    )
    max_tokens_per_chunk: int = field(
        default=Factory(lambda self: self.tokenizer.max_tokens, takes_self=True),
        kw_only=True
    )

    @abstractmethod
    def chunk(self, *args, **kwargs) -> list[str]:
        ...

    def chunk_recursively(self, chunk: str) -> list[str]:
        token_count = self.tokenizer.token_count(chunk)

        if token_count <= self.max_tokens_per_chunk:
            return [chunk]

        balance_index = -1
        balance_diff = float("inf")
        tokens_count = 0
        half_token_count = token_count // 2

        for splitter in self.separators:
            split_string = chunk.split(splitter)

            if len(split_string) > 1:
                for index, subchunk in enumerate(split_string):
                    subchunk = subchunk + splitter

                    tokens_count += self.tokenizer.token_count(subchunk)

                    if abs(tokens_count - half_token_count) < balance_diff:
                        balance_index = index
                        balance_diff = abs(tokens_count - half_token_count)

                first_chunk = " ".join(split_string[:balance_index + 1]).strip()
                second_chunk = " ".join(split_string[balance_index + 1:]).strip()

                return self.chunk_recursively(first_chunk) + self.chunk_recursively(second_chunk)
