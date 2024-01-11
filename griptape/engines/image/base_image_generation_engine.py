from __future__ import annotations

from attr import field, define

from griptape.drivers import BaseImageGenerationDriver
from griptape.rules import Ruleset


@define
class BaseImageGenerationEngine:
    image_generation_driver: BaseImageGenerationDriver = field(kw_only=True)

    def _ruleset_to_prompts(self, prompts: Optional[list[str]], rulesets: Optional[list[Ruleset]]) -> list[str]:
        if not prompts:
            prompts = []

        if rulesets:
            for ruleset in rulesets:
                prompts += [rule.value for rule in ruleset.rules]

        return prompts
