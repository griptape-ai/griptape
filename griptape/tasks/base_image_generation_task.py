from __future__ import annotations

import os

from attr import field, define

from griptape.artifacts import ImageArtifact
from griptape.engines import ImageGenerationEngine
from griptape.loaders.image_loader import ImageLoader
from griptape.rules import Ruleset, Rule
from griptape.tasks import BaseTextInputTask


@define
class BaseImageGenerationTask(BaseTextInputTask):
    """Provides a base class for image generation-related tasks.

    Attributes:
        image_generation_engine: The engine used to generate the image.
        negative_rulesets: List of negatively-weighted rulesets applied to the text prompt, if supported by the driver.
        negative_rules: List of negatively-weighted rules applied to the text prompt, if supported by the driver.
        output_dir: If provided, the generated image will be written to disk in output_dir.
        output_file: If provided, the generated image will be written to disk as output_file.
    """

    NEGATIVE_RULESET_NAME = "Negative Ruleset"

    image_generation_engine: ImageGenerationEngine = field(kw_only=True)
    negative_rulesets: list[Ruleset] = field(factory=list, kw_only=True)
    negative_rules: list[Rule] = field(factory=list, kw_only=True)
    output_dir: str | None = field(default=None, kw_only=True)
    output_file: str | None = field(default=None, kw_only=True)

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

    def _read_from_file(self, path: str) -> ImageArtifact:
        self.structure.logger.info(f"Reading image from {os.path.abspath(path)}")
        return ImageLoader().load(path)

    def _write_to_file(self, image_artifact: ImageArtifact) -> None:
        # Save image to file. This is a temporary workaround until we update Task and Meta
        # Memory to persist artifacts from tasks.
        if self.output_file is not None:
            outfile = self.output_file
        else:
            outfile = os.path.join(self.output_dir, image_artifact.name)

        if os.path.dirname(outfile):
            os.makedirs(os.path.dirname(outfile), exist_ok=True)

        with open(outfile, "wb") as f:
            self.structure.logger.info(f"Saving [{image_artifact.to_text()}] to {os.path.abspath(outfile)}")
            f.write(image_artifact.value)
