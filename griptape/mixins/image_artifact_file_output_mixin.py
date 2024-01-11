from __future__ import annotations

import os
from typing import TYPE_CHECKING

from attr import define, field

if TYPE_CHECKING:
    from griptape.artifacts import ImageArtifact


@define(slots=False)
class ImageArtifactFileOutputMixin:
    output_dir: Optional[str] = field(default=None, kw_only=True)
    output_file: Optional[str] = field(default=None, kw_only=True)

    @output_dir.validator  # pyright: ignore
    def validate_output_dir(self, _, output_dir: str) -> None:
        if not output_dir:
            return

        if self.output_file:
            raise ValueError("Can't have both output_dir and output_file specified.")

    @output_file.validator  # pyright: ignore
    def validate_output_file(self, _, output_file: str) -> None:
        if not output_file:
            return

        if self.output_dir:
            raise ValueError("Can't have both output_dir and output_file specified.")

    def _write_to_file(self, artifact: ImageArtifact) -> None:
        if self.output_file:
            outfile = self.output_file
        elif self.output_dir:
            outfile = os.path.join(self.output_dir, artifact.name)
        else:
            raise ValueError("No output_file or output_dir specified.")

        if os.path.dirname(outfile):
            os.makedirs(os.path.dirname(outfile), exist_ok=True)

        with open(outfile, "wb") as f:
            f.write(artifact.value)
