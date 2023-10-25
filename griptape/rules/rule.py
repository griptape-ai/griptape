from __future__ import annotations
from attr import define


@define(frozen=True)
class Rule:
    value: str
