from abc import ABC, abstractmethod
from attr import define, field
from typing import Any


class BasePromptStackProcessor(ABC):
    @abstractmethod
    def before_run(self, prompt: str) -> None:
        ...

    @abstractmethod
    def after_run(self, result: Any) -> Any:
        ...


@define
class BasePiiProcessor(BasePromptStackProcessor):
    pii_replace_text: str = field(default="[PII]", kw_only=True)
