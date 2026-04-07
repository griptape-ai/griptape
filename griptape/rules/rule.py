from __future__ import annotations

from attrs import define, field

from griptape.rules import BaseRule


@define()
class Rule(BaseRule):
    value: str = field(metadata={"serializable": True})

    def to_text(self) -> str:
        return self.value
