from __future__ import annotations

import os
import random
import string
import time
from os import path
from attr import define, field
from griptape.artifacts import ImageArtifact
from griptape.engines import ImageGenerationEngine
from griptape.rules import Rule, Ruleset
from griptape.tasks import BaseTextInputTask


@define
class ImageGenerationTask(BaseTextInputTask):
    NEGATIVE_RULESET_NAME = "Negative Ruleset"

    image_generation_engine: ImageGenerationEngine = field(kw_only=True)
    output_dir: str = field(kw_only=True)
    negative_rulesets: list[Ruleset] = field(factory=list, kw_only=True)
    negative_rules: list[Rule] = field(factory=list, kw_only=True)

    @negative_rulesets.validator
    def validate_negative_rulesets(self, _, negative_rulesets: list[Ruleset]) -> None:
        if not negative_rulesets:
            return

        if self.negative_rules:
            raise ValueError("Can't have both negative_rulesets and negative_rules specified.")

    @negative_rules.validator
    def validate_negative_rules(self, _, negative_rules: list[Rule]) -> None:
        if not negative_rules:
            return

        if self.negative_rulesets:
            raise ValueError("Can't have both negative_rules and negative_rulesets specified.")

    @property
    def all_negative_rulesets(self) -> list[Ruleset]:
        task_rulesets = []
        if self.negative_rulesets:
            task_rulesets = self.negative_rulesets

        elif self.negative_rules:
            task_rulesets = [Ruleset(name=self.NEGATIVE_RULESET_NAME, rules=self.negative_rules)]

        return task_rulesets

    def run(self) -> ImageArtifact:
        image_artifact = self.image_generation_engine.generate_image(
            prompts=[self.input.to_text()], rulesets=self.all_rulesets, negative_rulesets=self.negative_rulesets
        )

        self._save_to_file(image_artifact)

        return image_artifact

    def _save_to_file(self, image_artifact: ImageArtifact) -> None:
        # Save image to file. This is a temporary workaround until we update Task and Meta
        # Memory to persist artifacts from tasks.
        entropy = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
        fmt_time = time.strftime("%y%m%d%H%M%S", time.localtime())
        outfile = path.join(self.output_dir, f"image_artifact_{fmt_time}_{entropy}.png")

        with open(outfile, "wb") as f:
            self.structure.logger.info(f"Saving [{image_artifact.to_text()}] to {os.path.abspath(outfile)}")
            f.write(image_artifact.value)
