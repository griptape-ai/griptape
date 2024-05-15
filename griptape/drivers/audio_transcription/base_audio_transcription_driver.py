from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from attr import define, field

from griptape.artifacts import TextArtifact, AudioArtifact
from griptape.events import StartAudioTranscriptionEvent, FinishAudioTranscriptionEvent
from griptape.mixins import ExponentialBackoffMixin, SerializableMixin

if TYPE_CHECKING:
    from griptape.structures import Structure


@define
class BaseAudioTranscriptionDriver(SerializableMixin, ExponentialBackoffMixin, ABC):
    model: str = field(kw_only=True, metadata={"serializable": True})
    structure: Optional[Structure] = field(default=None, kw_only=True)

    def before_run(self) -> None:
        if self.structure:
            self.structure.publish_event(StartAudioTranscriptionEvent())

    def after_run(self) -> None:
        if self.structure:
            self.structure.publish_event(FinishAudioTranscriptionEvent())

    def run_transcription(self, audio: AudioArtifact, prompts: Optional[list[str]] = None) -> TextArtifact:
        for attempt in self.retrying():
            with attempt:
                self.before_run()
                result = self.try_transcription(audio, prompts)
                self.after_run()

                return result

        else:
            raise Exception("Failed to run audio transcription")

    @abstractmethod
    def try_transcription(self, audio: AudioArtifact, prompts: Optional[list[str]] = None) -> TextArtifact:
        ...
