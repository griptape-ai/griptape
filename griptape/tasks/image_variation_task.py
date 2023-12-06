from __future__ import annotations

import os
from os import path
from typing import Optional

from attr import define, field

from griptape.artifacts import ImageArtifact
from griptape.engines.image.image_generation_engine import ImageGenerationEngine
from griptape.loaders.image_loader import ImageLoader
from griptape.rules import Rule, Ruleset
from griptape.tasks import BaseTextInputTask


@define
class ImageVariationTask(BaseTextInputTask):
    """A task that generates a variation of an image using a prompt.

    Attributes:
        image_generation_engine: The engine used to modify the input image.
        image_file: The path to the input image file.
        output_dir: If provided, the generated image will be written to disk in output_dir.
        output_file: If provided, the generated image will be written to disk in output_file.
    """

    NEGATIVE_RULESET_NAME = "Negative Ruleset"

    image_generation_engine: ImageGenerationEngine = field(kw_only=True)
    image_file: str = field(kw_only=True)
    output_dir: Optional[str] = field(default=None, kw_only=True)
    output_file: Optional[str] = field(default=None, kw_only=True)
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
        input_image_artifact = self._read_from_file(self.image_file)

        output_image_artifact = self.image_generation_engine.image_variation(
            prompts=[self.input.to_text()],
            image=input_image_artifact,
            rulesets=self.all_rulesets,
            negative_rulesets=self.negative_rulesets,
        )

        if self.output_dir is not None or self.output_file is not None:
            self._write_to_file(output_image_artifact)

        return output_image_artifact

    def _read_from_file(self, path: str) -> ImageArtifact:
        self.structure.logger.info(f"Reading image from {os.path.abspath(path)}")
        return ImageLoader().load(path)

    def _write_to_file(self, image_artifact: ImageArtifact) -> None:
        # Save image to file. This is a temporary workaround until we update Task and Meta
        # Memory to persist artifacts from tasks.
        if self.output_file is not None:
            outfile = self.output_file
        else:
            outfile = path.join(self.output_dir, image_artifact.name)

        with open(outfile, "wb") as f:
            self.structure.logger.info(f"Saving [{image_artifact.to_text()}] to {os.path.abspath(outfile)}")
            f.write(image_artifact.value)
