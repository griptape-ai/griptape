from attrs import define
from typing import Callable
from galaxybrain.completions.completion_result import CompletionResult


@define
class Rule():
    value: str
    validator: Callable[[CompletionResult], bool] = lambda v: True