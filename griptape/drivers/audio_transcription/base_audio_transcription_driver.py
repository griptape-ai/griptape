from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from attrs import define, field

from griptape.events import EventBus, FinishAudioTranscriptionEvent, StartAudioTranscriptionEvent
from griptape.mixins.exponential_backoff_mixin import ExponentialBackoffMixin
from griptape.mixins.serializable_mixin import SerializableMixin

if TYPE_CHECKING:
    from griptape.artifacts import AudioArtifact, TextArtifact


@define
class BaseAudioTranscriptionDriver(SerializableMixin, ExponentialBackoffMixin, ABC):
    model: str = field(kw_only=True, metadata={"serializable": True})

    def before_run(self) -> None:
        EventBus.publish_event(StartAudioTranscriptionEvent())

    def after_run(self) -> None:
        EventBus.publish_event(FinishAudioTranscriptionEvent())

    def run(self, audio: AudioArtifact, prompts: Optional[list[str]] = None) -> TextArtifact:
        for attempt in self.retrying():
            with attempt:
                self.before_run()
                result = self.try_run(audio, prompts)
                self.after_run()

                return result

        else:
            raise Exception("Failed to run audio transcription")

    @abstractmethod
    def try_run(self, audio: AudioArtifact, prompts: Optional[list[str]] = None) -> TextArtifact: ...
