from abc import ABC, abstractmethod
from itertools import islice
from typing import Generator

from attr import define, field


@define
class BaseTokenizer(ABC):
    DEFAULT_STOP_SEQUENCE = "Observation:"

    stop_sequence: str = field(default=DEFAULT_STOP_SEQUENCE, kw_only=True)

    @property
    @abstractmethod
    def max_tokens(self) -> int:
        ...

    def tokens_left(self, text: str) -> int:
        diff = self.max_tokens - self.token_count(text)

        if diff > 0:
            return diff
        else:
            return 0

    def token_count(self, text: str) -> int:
        return len(self.encode(text))

    def chunk_tokens(self, tokens: list[int]) -> Generator:
        it = iter(tokens)

        while batch := tuple(islice(it, self.max_tokens)):
            yield batch

    @abstractmethod
    def encode(self, text: str) -> list[int]:
        ...

    @abstractmethod
    def decode(self, tokens: list[int]) -> str:
        ...
