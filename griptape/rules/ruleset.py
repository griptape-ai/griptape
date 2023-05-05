from attr import field, define
from griptape.rules import Rule


@define
class Ruleset:
    name: str = field()
    rules: list[Rule] = field()
