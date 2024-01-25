from __future__ import annotations

import os
from abc import ABC

from attr import field, define

from griptape.artifacts import ImageArtifact
from griptape.loaders import ImageLoader
from griptape.mixins import RuleMixin, ImageArtifactFileOutputMixin
from griptape.rules import Ruleset, Rule
from griptape.tasks import BaseTask


@define
class BaseImageGenerationTask(ImageArtifactFileOutputMixin, RuleMixin, BaseTask, ABC):
    """Provides a base class for image generation-related tasks.

    Attributes:
        negative_rulesets: List of negatively-weighted rulesets applied to the text prompt, if supported by the driver.
        negative_rules: List of negatively-weighted rules applied to the text prompt, if supported by the driver.
        output_dir: If provided, the generated image will be written to disk in output_dir.
        output_file: If provided, the generated image will be written to disk as output_file.
    """

    NEGATIVE_RULESET_NAME = "Negative Ruleset"

    negative_rulesets: list[Ruleset] = field(factory=list, kw_only=True)
    negative_rules: list[Rule] = field(factory=list, kw_only=True)

    @negative_rulesets.validator  # pyright: ignore
    def validate_negative_rulesets(self, _, negative_rulesets: list[Ruleset]) -> None:
        if not negative_rulesets:
            return

        if self.negative_rules:
            raise ValueError("Can't have both negative_rulesets and negative_rules specified.")

    @negative_rules.validator  # pyright: ignore
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

    def _read_from_file(self, path: str) -> ImageArtifact:
        self.structure.logger.info(f"Reading image from {os.path.abspath(path)}")
        with open(path, "rb") as file:
            return ImageLoader().load(file.read())
