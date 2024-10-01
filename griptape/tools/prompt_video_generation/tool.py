from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field
from schema import Literal, Schema

from griptape.tools import BaseVideoGenerationTool
from griptape.utils.decorators import activity

if TYPE_CHECKING:
    from griptape.artifacts import ErrorArtifact, VideoArtifact
    from griptape.drivers import DreamMachineVideoGenerationDriver


@define
class PromptVideoGenerationTool(BaseVideoGenerationTool):
    """A tool that can be used to generate a video from a text prompt.

    Attributes:
        driver: The video generation driver used to generate the video.
        output_dir: If provided, the generated video will be written to disk in output_dir.
        output_file: If provided, the generated video will be written to disk as output_file.
    """

    driver: DreamMachineVideoGenerationDriver = field(kw_only=True)

    @activity(
        config={
            "description": "Generates a video from text prompts.",
            "schema": Schema(
                {
                    Literal("prompt", description=BaseVideoGenerationTool.PROMPT_DESCRIPTION): str,
                }
            ),
        },
    )
    def generate_video(self, params: dict[str, dict[str, str]]) -> VideoArtifact | ErrorArtifact:
        prompt = params["values"]["prompt"]

        output_artifact = self.driver.try_text_to_video(prompt)

        if self.output_dir or self.output_file:
            self.save_video_artifact(output_artifact)

        return output_artifact
