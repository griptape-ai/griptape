from attrs import define, field

from griptape.rules import Rule


@define
class Ruleset:
    name: str = field()
    rules: list[Rule] = field()
