from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

if TYPE_CHECKING:
    from griptape.rules import Rule


@define
class Ruleset:
    name: str = field()
    rules: list[Rule] = field()
