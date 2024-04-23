from __future__ import annotations

from attr import define

from griptape.artifacts.audio_artifact import AudioArtifact
from griptape.engines.audio.base_audio_generation_engine import BaseAudioGenerationEngine


@define
class TextToAudioGenerationEngine(BaseAudioGenerationEngine):
    def run(self, prompts: list[str], *args, **kwargs) -> AudioArtifact:
        return self.audio_generation_driver.try_text_to_audio(prompts=prompts)
