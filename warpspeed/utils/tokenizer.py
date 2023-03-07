from abc import ABC, abstractmethod
from typing import Optional


class Tokenizer(ABC):
    DEFAULT_STOP_TOKEN = "<|endoftext|>"

    model: str
    stop_token: str

    @abstractmethod
    def encode(self, text: str) -> list[int]:
        ...

    @abstractmethod
    def decode(self, tokens: list[int]) -> str:
        ...

    @abstractmethod
    def token_count(self, text: str) -> int:
        ...

    @abstractmethod
    def tokens_left(self, text: str) -> Optional[int]:
        ...

    @abstractmethod
    def encoding(self):
        ...

    @abstractmethod
    def max_tokens(self) -> Optional[int]:
        ...
