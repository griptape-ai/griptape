from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from attr import define, field

from griptape.artifacts.audio_artifact import AudioArtifact
from griptape.events.finish_audio_generation_event import FinishAudioGenerationEvent
from griptape.events.start_audio_generation_event import StartAudioGenerationEvent
from griptape.mixins import ExponentialBackoffMixin, SerializableMixin

if TYPE_CHECKING:
    from griptape.structures import Structure


@define
class BaseTextToSpeechDriver(SerializableMixin, ExponentialBackoffMixin, ABC):
    model: str = field(kw_only=True, metadata={"serializable": True})
    structure: Optional[Structure] = field(default=None, kw_only=True)

    def before_run(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> None:
        if self.structure:
            self.structure.publish_event(StartAudioGenerationEvent(prompts=prompts, negative_prompts=negative_prompts))

    def after_run(self) -> None:
        if self.structure:
            self.structure.publish_event(FinishAudioGenerationEvent())

    def run_text_to_audio(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> AudioArtifact:
        for attempt in self.retrying():
            with attempt:
                self.before_run(prompts, negative_prompts)
                result = self.try_text_to_audio(prompts, negative_prompts)
                self.after_run()

                return result

        else:
            raise Exception("Failed to run text to audio generation")

    @abstractmethod
    def try_text_to_audio(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> AudioArtifact:
        ...
