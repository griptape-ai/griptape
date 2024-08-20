from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from attrs import Factory, define, field

from griptape.configs import Defaults

if TYPE_CHECKING:
    from griptape.artifacts import ImageArtifact
    from griptape.drivers import BaseImageGenerationDriver
    from griptape.rules import Ruleset


@define
class BaseImageGenerationEngine(ABC):
    image_generation_driver: BaseImageGenerationDriver = field(
        kw_only=True, default=Factory(lambda: Defaults.drivers_config.image_generation_driver)
    )

    @abstractmethod
    def run(self, prompts: list[str], *args, rulesets: Optional[list[Ruleset]], **kwargs) -> ImageArtifact: ...

    def _ruleset_to_prompts(self, prompts: Optional[list[str]], rulesets: Optional[list[Ruleset]]) -> list[str]:
        if not prompts:
            prompts = []

        if rulesets:
            for ruleset in rulesets:
                prompts += [rule.value for rule in ruleset.rules]

        return prompts
