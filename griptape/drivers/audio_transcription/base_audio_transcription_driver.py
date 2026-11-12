from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from attrs import define, field

from griptape.events import EventBus, FinishAudioTranscriptionEvent, StartAudioTranscriptionEvent
from griptape.mixins.exponential_backoff_mixin import ExponentialBackoffMixin
from griptape.mixins.serializable_mixin import SerializableMixin

if TYPE_CHECKING:
    from griptape.artifacts import AudioArtifact, TextArtifact


@define
class BaseAudioTranscriptionDriver(SerializableMixin, ExponentialBackoffMixin, ABC):
    """Base Audio Transcription Driver.

    Attributes:
        model: The name of the model to use.
        extra_params: Extra parameters to pass to the model's transcription request.
    """

    model: str = field(kw_only=True, metadata={"serializable": True})
    extra_params: dict = field(factory=dict, kw_only=True, metadata={"serializable": True})

    def before_run(self) -> None:
        EventBus.publish_event(StartAudioTranscriptionEvent())

    def after_run(self) -> None:
        EventBus.publish_event(FinishAudioTranscriptionEvent())

    def run(self, audio: AudioArtifact, prompts: list[str] | None = None) -> TextArtifact:
        for attempt in self.retrying():
            with attempt:
                self.before_run()
                result = self.try_run(audio, prompts)
                self.after_run()

                return result

        raise Exception("Failed to run audio transcription")

    @abstractmethod
    def try_run(self, audio: AudioArtifact, prompts: list[str] | None = None) -> TextArtifact:
        pass
