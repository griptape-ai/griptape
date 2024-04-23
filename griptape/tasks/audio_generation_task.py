from __future__ import annotations

from typing import Callable

from attr import define, field

from griptape.artifacts.audio_artifact import AudioArtifact
from griptape.engines import TextToAudioGenerationEngine
from griptape.artifacts import TextArtifact
from griptape.tasks import BaseTask
from griptape.tasks.base_audio_generation_task import BaseAudioGenerationTask
from griptape.utils import J2


@define
class AudioGenerationTask(BaseAudioGenerationTask):
    DEFAULT_INPUT_TEMPLATE = "{{ args[0] }}"

    _input: str | TextArtifact | Callable[[BaseTask], TextArtifact] = field(default=DEFAULT_INPUT_TEMPLATE)
    _audio_generation_engine: TextToAudioGenerationEngine = field(
        default=None, kw_only=True, alias="audio_generation_engine"
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

    @property
    def audio_generation_engine(self) -> TextToAudioGenerationEngine:
        if self._audio_generation_engine is None:
            if self.structure is not None:
                self._audio_generation_engine = TextToAudioGenerationEngine(
                    audio_generation_driver=self.structure.config.global_drivers.audio_generation_driver
                )
            else:
                raise ValueError("Audio Generation Engine is not set.")
        return self._audio_generation_engine

    @audio_generation_engine.setter
    def audio_generation_engine(self, value: TextToAudioGenerationEngine) -> None:
        self._audio_generation_engine = value

    def run(self) -> AudioArtifact:
        audio_artifact = self.audio_generation_engine.run(prompts=[self.input.to_text()], rulesets=self.all_rulesets)

        if self.output_dir or self.output_file:
            self._write_to_file(audio_artifact)

        return audio_artifact
