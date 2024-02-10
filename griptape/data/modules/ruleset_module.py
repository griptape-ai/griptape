from attr import define, field
from griptape.data.modules import BaseModule
from griptape.rules import Ruleset
from griptape.utils import J2


@define
class RulesetModule(BaseModule):
    rulesets: list[Ruleset] = field(kw_only=True)

    def process(self, context: dict) -> dict:
        rules_text = J2("rulesets/rulesets.j2").render(rulesets=self.rulesets)

        if not context.get("before_text_query"):
            context["before_text_query"] = ""

        context["before_text_query"] += rules_text

        return context
