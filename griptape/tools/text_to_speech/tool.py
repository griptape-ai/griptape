from __future__ import annotations

from typing import TYPE_CHECKING, Any

from attrs import define, field
from schema import Literal, Schema

from griptape.artifacts import ListArtifact
from griptape.mixins.artifact_file_output_mixin import ArtifactFileOutputMixin
from griptape.tools import BaseTool
from griptape.utils.decorators import activity

if TYPE_CHECKING:
    from griptape.artifacts import AudioArtifact
    from griptape.engines import TextToSpeechEngine


@define
class TextToSpeechTool(ArtifactFileOutputMixin, BaseTool):
    """A tool that can be used to generate speech from input text.

    Attributes:
        engine: The text to audio generation engine used to generate the speech audio.
        output_dir: If provided, the generated audio will be written to disk in output_dir.
        output_file: If provided, the generated audio will be written to disk as output_file.
    """

    engine: TextToSpeechEngine = field(kw_only=True)

    @activity(
        config={
            "description": "Can be used to generate speech from the provided input text.",
            "schema": Schema({Literal("text", description="The literal text to be converted to speech."): str}),
        },
    )
    def text_to_speech(self, params: dict[str, Any]) -> ListArtifact[AudioArtifact]:
        text = params["values"]["text"]

        output_artifacts = self.engine.run(prompts=[text])

        if self.output_dir or self.output_file:
            for audio_artifact in output_artifacts:
                self._write_to_file(audio_artifact)

        return ListArtifact(output_artifacts)
