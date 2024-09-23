from __future__ import annotations

from typing import Callable

from attrs import Factory, define, field

from griptape.artifacts import TextArtifact, VideoArtifact
from griptape.drivers import DreamMachineVideoGenerationDriver
from griptape.tasks import BaseTask, BaseVideoGenerationTask
from griptape.utils import J2


@define
class PromptVideoGenerationTask(BaseVideoGenerationTask):
    """Used to generate a video from a text prompt.

    Accepts prompt as input in one of the following formats:
    - template string
    - TextArtifact
    - Callable that returns a TextArtifact.

    Attributes:
        video_generation_driver: The driver used to generate the video.
        negative_prompts: List of negatively-weighted prompts applied to the text prompt, if supported by the driver.
        output_dir: If provided, the generated video will be written to disk in output_dir.
        output_file: If provided, the generated video will be written to disk as output_file.
    """

    api_key: str = field(kw_only=True)
    DEFAULT_INPUT_TEMPLATE = "{{ args[0] }}"

    _input: str | TextArtifact | Callable[[BaseTask], TextArtifact] = field(
        default=DEFAULT_INPUT_TEMPLATE, alias="input"
    )
    video_generation_driver: DreamMachineVideoGenerationDriver = field(
        default=Factory(lambda self: DreamMachineVideoGenerationDriver(api_key=self.api_key), takes_self=True),
        kw_only=True,
    )

    @property
    def input(self) -> TextArtifact:
        if isinstance(self._input, TextArtifact):
            return self._input
        elif isinstance(self._input, Callable):
            return self._input(self)
        else:
            return TextArtifact(J2().render_from_string(self._input, **self.full_context))

    @input.setter
    def input(self, value: TextArtifact) -> None:
        self._input = value

    def run(self) -> VideoArtifact:
        video_artifact = self.video_generation_driver.try_text_to_video(prompt=self.input.to_text())

        if self.output_dir or self.output_file:
            self.save_artifact(video_artifact)

        return video_artifact
