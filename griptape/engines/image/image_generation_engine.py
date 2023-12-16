from __future__ import annotations

from typing import Optional

from attr import field, define

from griptape.artifacts import ImageArtifact
from griptape.drivers import BaseImageGenerationDriver
from griptape.rules import Ruleset


@define
class ImageGenerationEngine:
    image_driver: BaseImageGenerationDriver = field(kw_only=True)

    def text_to_image(
        self,
        prompts: list[str],
        negative_prompts: list[str] | None = None,
        rulesets: list[Ruleset] | None = None,
        negative_rulesets: list[Ruleset] | None = None,
    ) -> ImageArtifact:
        prompts = self._ruleset_to_prompts(prompts, rulesets)
        negative_prompts = self._ruleset_to_prompts(negative_prompts, negative_rulesets)

        return self.image_driver.run_text_to_image(prompts, negative_prompts=negative_prompts)

    def image_variation(
        self,
        prompts: list[str],
        image: ImageArtifact,
        negative_prompts: list[str] | None = None,
        rulesets: list[Ruleset] | None = None,
        negative_rulesets: list[Ruleset] | None = None,
    ) -> ImageArtifact:
        prompts = self._ruleset_to_prompts(prompts, rulesets)
        negative_prompts = self._ruleset_to_prompts(negative_prompts, negative_rulesets)

        return self.image_driver.run_image_variation(prompts=prompts, image=image, negative_prompts=negative_prompts)

    def image_inpainting(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: list[str] | None = None,
        rulesets: list[Ruleset] | None = None,
        negative_rulesets: list[Ruleset] | None = None,
    ) -> ImageArtifact:
        prompts = self._ruleset_to_prompts(prompts, rulesets)
        negative_prompts = self._ruleset_to_prompts(negative_prompts, negative_rulesets)

        return self.image_driver.run_image_inpainting(
            prompts, image=image, mask=mask, negative_prompts=negative_prompts
        )

    def image_outpainting(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: list[str] | None = None,
        rulesets: list[Ruleset] | None = None,
        negative_rulesets: list[Ruleset] | None = None,
    ) -> ImageArtifact:
        prompts = self._ruleset_to_prompts(prompts, rulesets)
        negative_prompts = self._ruleset_to_prompts(negative_prompts, negative_rulesets)

        return self.image_driver.run_image_outpainting(
            prompts, image=image, mask=mask, negative_prompts=negative_prompts
        )

    def _ruleset_to_prompts(self, prompts: list[str] | None, rulesets: list[Ruleset] | None) -> list[str]:
        if not prompts:
            prompts = []

        if rulesets:
            for ruleset in rulesets:
                prompts += [rule.value for rule in ruleset.rules]

        return prompts
