from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from griptape.engines.rag.modules import BaseBeforeResponseRagModule
from griptape.utils import J2

if TYPE_CHECKING:
    from griptape.engines.rag import RagContext
    from griptape.rules import Ruleset


@define
class RulesetsBeforeResponseRagModule(BaseBeforeResponseRagModule):
    rulesets: list[Ruleset] = field(kw_only=True)

    def run(self, context: RagContext) -> RagContext:
        context.before_query.append(J2("rulesets/rulesets.j2").render(rulesets=self.rulesets))

        return context
