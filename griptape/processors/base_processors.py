from abc import ABC, abstractmethod
from attr import define, field
from typing import Any


@define
class BasePromptStackProcessor(ABC):
    pii_replace_text: str = field(default="[PII]", kw_only=True)

    @abstractmethod
    def before_run(self, prompt: str) -> str:
        ...

    @abstractmethod
    def after_run(self, result: Any) -> Any:
        ...
