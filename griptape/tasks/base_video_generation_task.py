from __future__ import annotations

import logging
import os
from abc import ABC
from pathlib import Path
from typing import TYPE_CHECKING

from attrs import define

from griptape.configs import Defaults
from griptape.loaders import VideoLoader
from griptape.mixins.artifact_file_output_mixin import ArtifactFileOutputMixin
from griptape.tasks import BaseTask

if TYPE_CHECKING:
    from griptape.artifacts import VideoArtifact

logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class BaseVideoGenerationTask(ArtifactFileOutputMixin, BaseTask, ABC):
    """Provides a base class for video generation-related tasks.

    Attributes:
        output_dir: If provided, the generated video will be written to disk in output_dir.
        output_file: If provided, the generated video will be written to disk as output_file.
    """

    def save_artifact(self, artifact: VideoArtifact) -> None:
        if self.output_file:
            outfile = self.output_file
        elif self.output_dir:
            outfile = os.path.join(self.output_dir, artifact.name + ".mp4")
        else:
            raise ValueError("No output_file or output_dir specified.")

        if os.path.dirname(outfile):
            os.makedirs(os.path.dirname(outfile), exist_ok=True)

        Path(outfile).write_bytes(artifact.to_bytes())

    def _read_from_file(self, path: str) -> VideoArtifact:
        logger.info("Reading video from %s", os.path.abspath(path))
        return VideoLoader().load(Path(path).read_bytes())
