from __future__ import annotations

from abc import abstractmethod
from attr import define

from griptape.rules import Ruleset
from griptape.artifacts import ImageArtifact
from griptape.engines import BaseImageGenerationEngine


@define
class PromptImageGenerationEngine(BaseImageGenerationEngine):
    def run(
        self,
        prompts: list[str],
        negative_prompts: Optional[list[str]] = None,
        rulesets: Optional[list[Ruleset]] = None,
        negative_rulesets: Optional[list[Ruleset]] = None,
    ) -> ImageArtifact:
        prompts = self._ruleset_to_prompts(prompts, rulesets)
        negative_prompts = self._ruleset_to_prompts(negative_prompts, negative_rulesets)

        return self.image_generation_driver.run_text_to_image(prompts, negative_prompts=negative_prompts)
