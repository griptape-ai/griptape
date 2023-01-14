from attrs import define
from typing import Callable, Optional


@define
class PromptRule():
    value: str
    validator: Callable[[str], bool] = lambda v: True