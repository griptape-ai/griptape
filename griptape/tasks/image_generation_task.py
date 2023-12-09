from __future__ import annotations

import os
from os import path
from typing import Optional

from attr import define, field
from griptape.artifacts import ImageArtifact
from griptape.engines import ImageGenerationEngine
from griptape.rules import Rule, Ruleset
from griptape.tasks import BaseTextInputTask


@define
class ImageGenerationTask(BaseTextInputTask):
    """ImageGenerationTask is a task that can be used to generate an image.

    Attributes:
        image_generation_engine: The engine used to generate the image.
        output_dir: If provided, the generated image will be written to disk in output_dir.
        output_file: If provided, the generated image will be written to disk as output_file.
    """

    NEGATIVE_RULESET_NAME = "Negative Ruleset"

    image_generation_engine: ImageGenerationEngine = field(kw_only=True)
    output_dir: str | None = field(default=None, kw_only=True)
    output_file: str | None = field(default=None, kw_only=True)
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

    @output_dir.validator
    def validate_output_dir(self, _, output_dir: str) -> None:
        if not output_dir:
            return

        if self.output_file:
            raise ValueError("Can't have both output_dir and output_file specified.")

    @output_file.validator
    def validate_output_file(self, _, output_file: str) -> None:
        if not output_file:
            return

        if self.output_dir:
            raise ValueError("Can't have both output_dir and output_file specified.")

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

        if self.output_dir or self.output_file:
            self._write_to_file(image_artifact)

        return image_artifact

    def _write_to_file(self, image_artifact: ImageArtifact) -> None:
        # Save image to file. This is a temporary workaround until we update Task and Meta
        # Memory to persist artifacts from tasks.
        if self.output_file:
            outfile = self.output_file
        else:
            outfile = path.join(self.output_dir, image_artifact.name)

        os.makedirs(path.dirname(outfile), exist_ok=True)
        with open(outfile, "wb") as f:
            self.structure.logger.info(f"Saving [{image_artifact.to_text()}] to {os.path.abspath(outfile)}")
            f.write(image_artifact.value)
