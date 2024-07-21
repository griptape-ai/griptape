from __future__ import annotations

from typing import TYPE_CHECKING, Any

from attrs import define, field
from schema import Literal, Schema

from griptape.mixins import BlobArtifactFileOutputMixin
from griptape.tools import BaseTool
from griptape.utils.decorators import activity

if TYPE_CHECKING:
    from griptape.artifacts import AudioArtifact, ErrorArtifact
    from griptape.engines import TextToSpeechEngine


@define
class TextToSpeechClient(BlobArtifactFileOutputMixin, BaseTool):
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
    def text_to_speech(self, params: dict[str, Any]) -> AudioArtifact | ErrorArtifact:
        text = params["values"]["text"]

        output_artifact = self.engine.run(prompts=[text])

        if self.output_dir or self.output_file:
            self._write_to_file(output_artifact)

        return output_artifact
