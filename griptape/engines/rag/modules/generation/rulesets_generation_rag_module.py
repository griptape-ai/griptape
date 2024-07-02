from attrs import define, field
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseBeforeGenerationRagModule
from griptape.rules import Ruleset
from griptape.utils import J2


@define
class RulesetsGenerationRagModule(BaseBeforeGenerationRagModule):
    rulesets: list[Ruleset] = field(kw_only=True)

    def run(self, context: RagContext) -> RagContext:
        context.before_query.append(J2("rulesets/rulesets.j2").render(rulesets=self.rulesets))

        return context
