from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from attrs import Factory, define, field

from griptape.configs import Defaults

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

    def __attrs_post_init__(self) -> None:
        rules, meta = self.ruleset_driver.load(self.name)
        self.rules = [*rules, *self.rules]
        self.meta = {**meta, **self.meta}
