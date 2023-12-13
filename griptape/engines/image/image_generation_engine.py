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
        negative_prompts: Optional[list[str]] = None,
        rulesets: Optional[list[Ruleset]] = None,
        negative_rulesets: Optional[list[Ruleset]] = None,
    ) -> ImageArtifact:
        if not negative_prompts:
            negative_prompts = []

        if rulesets:
            for ruleset in rulesets:
                prompts += [rule.value for rule in ruleset.rules]

        if negative_rulesets:
            for negative_ruleset in negative_rulesets:
                negative_prompts += [rule.value for rule in negative_ruleset.rules]

        return self.image_driver.run_text_to_image(prompts, negative_prompts=negative_prompts)

    def image_variation(
        self,
        prompts: list[str],
        image: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
        rulesets: Optional[list[Ruleset]] = None,
        negative_rulesets: Optional[list[Ruleset]] = None,
    ) -> ImageArtifact:
        if not negative_prompts:
            negative_prompts = []

        if rulesets:
            for ruleset in rulesets:
                prompts += [rule.value for rule in ruleset.rules]

        if negative_rulesets:
            for negative_ruleset in negative_rulesets:
                negative_prompts += [rule.value for rule in negative_ruleset.rules]

        return self.image_driver.run_image_variation(prompts=prompts, image=image, negative_prompts=negative_prompts)

    def image_inpainting(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
        rulesets: Optional[list[Ruleset]] = None,
        negative_rulesets: Optional[list[Ruleset]] = None,
    ) -> ImageArtifact:
        if not negative_prompts:
            negative_prompts = []

        if rulesets:
            for ruleset in rulesets:
                prompts += [rule.value for rule in ruleset.rules]

        if negative_rulesets:
            for negative_ruleset in negative_rulesets:
                negative_prompts += [rule.value for rule in negative_ruleset.rules]

        return self.image_driver.run_image_inpainting(
            prompts, image=image, mask=mask, negative_prompts=negative_prompts
        )

    def image_outpainting(
        self,
        prompts: list[str],
        image: ImageArtifact,
        mask: ImageArtifact,
        negative_prompts: Optional[list[str]] = None,
        rulesets: Optional[list[Ruleset]] = None,
        negative_rulesets: Optional[list[Ruleset]] = None,
    ) -> ImageArtifact:
        if not negative_prompts:
            negative_prompts = []

        if rulesets:
            for ruleset in rulesets:
                prompts += [rule.value for rule in ruleset.rules]

        if negative_rulesets:
            for negative_ruleset in negative_rulesets:
                negative_prompts += [rule.value for rule in negative_ruleset.rules]

        return self.image_driver.run_image_outpainting(
            prompts, image=image, mask=mask, negative_prompts=negative_prompts
        )
