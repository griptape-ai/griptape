from __future__ import annotations

from attrs import define, field

from griptape.rules import BaseRule


@define(frozen=True)
class Rule(BaseRule):
    value: str = field()

    def to_text(self) -> str:
        return self.value
