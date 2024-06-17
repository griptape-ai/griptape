from __future__ import annotations

from abc import ABC

from attrs import define

from griptape.mixins import RuleMixin, BlobArtifactFileOutputMixin
from griptape.tasks import BaseTask


@define
class BaseAudioGenerationTask(BlobArtifactFileOutputMixin, RuleMixin, BaseTask, ABC):
    def before_run(self) -> None:
        super().before_run()

        self.structure.logger.info(f"{self.__class__.__name__} {self.id}\nInput: {self.input.to_text()}")

    def after_run(self) -> None:
        super().after_run()

        self.structure.logger.info(f"{self.__class__.__name__} {self.id}\nOutput: {self.output.to_text()}")
