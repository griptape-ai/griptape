from __future__ import annotations

from attrs import define


@define(frozen=True)
class Rule:
    value: str
