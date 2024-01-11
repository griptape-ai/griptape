from __future__ import annotations

from attr import define

from griptape.engines import BaseImageGenerationEngine
from griptape.artifacts import ImageArtifact
from griptape.rules import Ruleset


@define
class InpaintingImageGenerationEngine(BaseImageGenerationEngine):
    def run(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
        rulesets: Optional[list[Ruleset]] = None,
        negative_rulesets: Optional[list[Ruleset]] = None,
    ) -> ImageArtifact:
        prompts = self._ruleset_to_prompts(prompts, rulesets)
        negative_prompts = self._ruleset_to_prompts(negative_prompts, negative_rulesets)

        return self.image_generation_driver.run_image_inpainting(
            prompts, image=image, mask=mask, negative_prompts=negative_prompts
        )
