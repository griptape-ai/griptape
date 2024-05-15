from __future__ import annotations

from typing import Any, cast

from attrs import define, field, Factory
from schema import Schema, Literal

from griptape.artifacts import ErrorArtifact, AudioArtifact, TextArtifact
from griptape.drivers import BaseAudioTranscriptionDriver
from griptape.loaders.audio_loader import AudioLoader
from griptape.tools import BaseTool
from griptape.utils import load_artifact_from_memory
from griptape.utils.decorators import activity


@define
class TranscriptionClient(BaseTool):
    """A tool that can be used to generate transcriptions from input audio."""

    driver: BaseAudioTranscriptionDriver = field(kw_only=True)
    audio_loader: AudioLoader = field(default=Factory(lambda: AudioLoader()), kw_only=True)

    @activity(
        config={
            "description": "This tool can be used to generate transcriptions of audio files on disk.",
            "schema": Schema({Literal("path", description="The paths to an audio file on disk."): str}),
        }
    )
    def transcribe_audio_from_disk(self, params: dict) -> TextArtifact | ErrorArtifact:
        audio_path = params["values"]["path"]

        with open(audio_path, "rb") as f:
            audio_artifact = self.audio_loader.load(f.read())

        return self.driver.run_transcription(audio_artifact)

    @activity(
        config={
            "description": "This tool can be used to generate the transcription of an audio artifact in memory.",
            "schema": Schema({"schema": Schema({"memory_name": str, "artifact_namespace": str, "artifact_name": str})}),
        }
    )
    def transcribe_audio_from_memory(self, params: dict[str, Any]) -> TextArtifact | ErrorArtifact:
        memory = self.find_input_memory(params["values"]["memory_name"])
        artifact_namespace = params["values"]["artifact_namespace"]
        artifact_name = params["values"]["artifact_name"]

        if memory is None:
            return ErrorArtifact("memory not found")

        audio_artifact = cast(
            AudioArtifact, load_artifact_from_memory(memory, artifact_namespace, artifact_name, AudioArtifact)
        )

        return self.driver.run_transcription(audio_artifact)
