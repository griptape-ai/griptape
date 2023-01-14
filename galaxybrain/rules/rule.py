from attrs import define
from typing import Callable


@define
class Rule():
    value: str
    validator: Callable[[str], bool] = lambda v: True