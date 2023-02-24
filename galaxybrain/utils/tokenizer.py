from abc import ABC, abstractmethod
from typing import Optional


class Tokenizer(ABC):
    model: str
    stop_token: str

    @abstractmethod
    def encode(self, text: str) -> list[int]:
        pass

    @abstractmethod
    def decode(self, tokens: list[int]) -> str:
        pass

    @abstractmethod
    def token_count(self, text: str) -> int:
        pass

    @abstractmethod
    def tokens_left(self, text: str) -> Optional[int]:
        pass

    @abstractmethod
    def encoding(self):
        pass

    @abstractmethod
    def max_tokens(self) -> Optional[int]:
        pass
