from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from attrs import define, field

from griptape.mixins.serializable_mixin import SerializableMixin


@define()
class BaseRule(ABC, SerializableMixin):
    value: Any = field(metadata={"serializable": True})
    meta: dict[str, Any] = field(factory=dict, kw_only=True)

    def __str__(self) -> str:
        return self.to_text()

    @abstractmethod
    def to_text(self) -> str: ...
