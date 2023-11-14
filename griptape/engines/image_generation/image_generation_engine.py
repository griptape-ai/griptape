from attr import field, define
from griptape.drivers import BaseImageGenerationDriver
from griptape.rules import Rule, Ruleset


@define
class ImageGenerationEngine:
    image_generation_driver: BaseImageGenerationDriver = field(kw_only=True)

    def generate_image(
        self,
        prompts: list[str],
        negative_prompts: list[str] = list,
        rulesets: list[Ruleset] = list,
        negative_rulesets: list[Ruleset] = list,
        **kwargs
    ):
        for ruleset in rulesets:
            prompts += [rule.value for rule in ruleset.rules]

        for negative_ruleset in negative_rulesets:
            negative_prompts += [rule.value for rule in negative_ruleset.rules]

        return self.image_generation_driver.generate_image(prompts, negative_prompts, **kwargs)
