from __future__ import annotations

import logging
from abc import ABC

from attrs import define

from griptape.configs import Defaults
from griptape.mixins.artifact_file_output_mixin import ArtifactFileOutputMixin
from griptape.mixins.rule_mixin import RuleMixin
from griptape.tasks import BaseTask

logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class BaseAudioGenerationTask(ArtifactFileOutputMixin, RuleMixin, BaseTask, ABC):
    def before_run(self) -> None:
        super().before_run()

        logger.info("%s %s\nInput: %s", self.__class__.__name__, self.id, self.input.to_text())

    def after_run(self) -> None:
        super().after_run()

        logger.info(
            "%s %s\nOutput: %s",
            self.__class__.__name__,
            self.id,
            self.output.to_text() if self.output is not None else "",
        )
