from __future__ import annotations

from attrs import define
from typing import Optional, TYPE_CHECKING

from griptape.engines import BaseImageGenerationEngine

if TYPE_CHECKING:
    from griptape.rules import Ruleset
    from griptape.artifacts import ImageArtifact


@define
class PromptImageGenerationEngine(BaseImageGenerationEngine):
    def run(
        self,
        prompts: list[str],
        *args,
        negative_prompts: Optional[list[str]] = None,
        rulesets: Optional[list[Ruleset]] = None,
        negative_rulesets: Optional[list[Ruleset]] = None,
        **kwargs,
    ) -> ImageArtifact:
        prompts = self._ruleset_to_prompts(prompts, rulesets)
        negative_prompts = self._ruleset_to_prompts(negative_prompts, negative_rulesets)

        return self.image_generation_driver.run_text_to_image(prompts, negative_prompts=negative_prompts)
