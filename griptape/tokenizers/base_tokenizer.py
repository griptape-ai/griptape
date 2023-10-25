from abc import ABC, abstractmethod
from attr import define, field, Factory


@define(frozen=True)
class BaseTokenizer(ABC):
    DEFAULT_STOP_SEQUENCES = ["Observation:"]

    stop_sequences: list[str] = field(
        default=Factory(lambda: BaseTokenizer.DEFAULT_STOP_SEQUENCES),
        kw_only=True,
    )

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

    @abstractmethod
    def token_count(self, text: str) -> int:
        ...
