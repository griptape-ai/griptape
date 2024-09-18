from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

from attrs import define, field

if TYPE_CHECKING:
    from griptape.rules import BaseRule


@define
class Ruleset:
    name: str = field()
    rules: Sequence[BaseRule] = field()
