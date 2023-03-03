from __future__ import annotations
from typing import TYPE_CHECKING
from attrs import define
from typing import Callable

if TYPE_CHECKING:
    from galaxybrain.artifacts import StepOutput


@define(frozen=True)
class Rule:
    value: str
    validator: Callable[[StepOutput], bool] = lambda v: True
