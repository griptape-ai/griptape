from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Callable, Union

from attrs import Factory, define, field

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

    _input: Union[str, TextArtifact, Callable[[BaseTask], TextArtifact]] = field(default=DEFAULT_INPUT_TEMPLATE)
    text_to_speech_engine: TextToSpeechEngine = field(default=Factory(lambda: TextToSpeechEngine()), kw_only=True)

    @cached_property
    def input(self) -> TextArtifact:
        if isinstance(self._input, TextArtifact):
            return self._input
        elif isinstance(self._input, Callable):
            return self._input(self)
        else:
            return TextArtifact(J2().render_from_string(self._input, **self.full_context))

    def try_run(self) -> AudioArtifact:
        audio_artifact = self.text_to_speech_engine.run(prompts=[self.input.to_text()], rulesets=self.rulesets)

        if self.output_dir or self.output_file:
            self._write_to_file(audio_artifact)

        return audio_artifact
