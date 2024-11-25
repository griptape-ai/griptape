from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, Callable, Optional

from attrs import Factory, define, field

from griptape.configs import Defaults
from griptape.engines import EvalEngine
from griptape.utils.j2 import J2

if TYPE_CHECKING:
    from collections.abc import Sequence

    from griptape.drivers import BaseRulesetDriver
    from griptape.rules import BaseRule


@define
class Ruleset:
    id: str = field(default=Factory(lambda: uuid.uuid4().hex), kw_only=True)
    name: str = field(
        default=Factory(lambda self: self.id, takes_self=True),
        metadata={"serializable": True},
    )
    ruleset_driver: BaseRulesetDriver = field(
        default=Factory(lambda: Defaults.drivers_config.ruleset_driver), kw_only=True
    )
    meta: dict[str, Any] = field(factory=dict, kw_only=True)
    rules: Sequence[BaseRule] = field(factory=list)
    generate_system_template: Callable[[Ruleset], str] = field(
        default=Factory(lambda: lambda self: J2("rulesets/ruleset.j2").render(ruleset=self)),
        kw_only=True,
    )
    eval_engine: Optional[EvalEngine] = field(
        default=Factory(
            lambda self: EvalEngine(id=f"{self.name} Eval Engine", criteria=self.to_text()), takes_self=True
        ),
        kw_only=True,
    )

    def __attrs_post_init__(self) -> None:
        rules, meta = self.ruleset_driver.load(self.name)
        self.rules = [*rules, *self.rules]
        self.meta = {**meta, **self.meta}

    def __str__(self) -> str:
        return self.to_text()

    def to_text(self) -> str:
        return self.generate_system_template(self)

    def evaluate(self, **kwargs) -> tuple[float, str]:
        if self.eval_engine is None:
            raise ValueError("eval_engine is not set")

        return self.eval_engine.evaluate(**kwargs)
