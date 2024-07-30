from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from attrs import define, field

from griptape.artifacts import TextArtifact
from griptape.engines import TextToSpeechEngine
from griptape.tasks.base_audio_generation_task import BaseAudioGenerationTask
from griptape.utils import J2

if TYPE_CHECKING:
    from griptape.artifacts.audio_artifact import AudioArtifact
    from griptape.tasks import BaseTask


@define
class TextToSpeechTask(BaseAudioGenerationTask):
    DEFAULT_INPUT_TEMPLATE = "{{ args[0] }}"

    _input: str | TextArtifact | Callable[[BaseTask], TextArtifact] = field(default=DEFAULT_INPUT_TEMPLATE)
    _text_to_speech_engine: TextToSpeechEngine = field(default=None, kw_only=True, alias="text_to_speech_engine")

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
    def text_to_speech_engine(self) -> TextToSpeechEngine:
        if self._text_to_speech_engine is None:
            if self.structure is not None:
                self._text_to_speech_engine = TextToSpeechEngine(
                    text_to_speech_driver=self.structure.config.text_to_speech_driver,
                )
            else:
                raise ValueError("Audio Generation Engine is not set.")
        return self._text_to_speech_engine

    @text_to_speech_engine.setter
    def text_to_speech_engine(self, value: TextToSpeechEngine) -> None:
        self._text_to_speech_engine = value

    def run(self) -> AudioArtifact:
        audio_artifact = self.text_to_speech_engine.run(prompts=[self.input.to_text()], rulesets=self.all_rulesets)

        if self.output_dir or self.output_file:
            self._write_to_file(audio_artifact)

        return audio_artifact
