from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from attrs import Factory, define, field
from schema import Literal, Schema

from griptape.artifacts import AudioArtifact, ErrorArtifact, TextArtifact
from griptape.drivers.audio_transcription import BaseAudioTranscriptionDriver
from griptape.loaders import AudioLoader
from griptape.tools import BaseTool
from griptape.utils import load_artifact_from_memory
from griptape.utils.decorators import activity

if TYPE_CHECKING:
    from griptape.drivers.audio_transcription import BaseAudioTranscriptionDriver


@define
class AudioTranscriptionTool(BaseTool):
    """A tool that can be used to generate transcriptions from input audio."""

    audio_transcription_driver: BaseAudioTranscriptionDriver = field(kw_only=True)
    audio_loader: AudioLoader = field(default=Factory(lambda: AudioLoader()), kw_only=True)

    @activity(
        config={
            "description": "This tool can be used to generate transcriptions of audio files on disk.",
            "schema": Schema({Literal("path", description="The paths to an audio file on disk."): str}),
        },
    )
    def transcribe_audio_from_disk(self, params: dict) -> TextArtifact | ErrorArtifact:
        audio_path = params["values"]["path"]

        audio_artifact = self.audio_loader.load(audio_path)

        return self.audio_transcription_driver.run(audio_artifact)

    @activity(
        config={
            "description": "This tool can be used to generate the transcription of an audio artifact in memory.",
            "schema": Schema({"schema": Schema({"memory_name": str, "artifact_namespace": str, "artifact_name": str})}),
        },
    )
    def transcribe_audio_from_memory(self, params: dict[str, Any]) -> TextArtifact | ErrorArtifact:
        memory = self.find_input_memory(params["values"]["memory_name"])
        artifact_namespace = params["values"]["artifact_namespace"]
        artifact_name = params["values"]["artifact_name"]

        if memory is None:
            return ErrorArtifact("memory not found")

        audio_artifact = cast(
            "AudioArtifact",
            load_artifact_from_memory(memory, artifact_namespace, artifact_name, AudioArtifact),
        )

        return self.audio_transcription_driver.run(audio_artifact)
