from __future__ import annotations

from abc import ABC

from attrs import define

from griptape.mixins import BlobArtifactFileOutputMixin, RuleMixin
from griptape.tasks import BaseTask


@define
class BaseAudioGenerationTask(BlobArtifactFileOutputMixin, RuleMixin, BaseTask, ABC):
    def before_run(self) -> None:
        super().before_run()

        self.structure.logger.info("%s %s\nInput: %s", self.__class__.__name__, self.id, self.input.to_text())

    def after_run(self) -> None:
        super().after_run()

        self.structure.logger.info("%s %s\nOutput: %s", self.__class__.__name__, self.id, self.output.to_text())
