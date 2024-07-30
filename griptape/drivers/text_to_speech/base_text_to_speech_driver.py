from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from attrs import define, field

from griptape.events.finish_text_to_speech_event import FinishTextToSpeechEvent
from griptape.events.start_text_to_speech_event import StartTextToSpeechEvent
from griptape.mixins import EventPublisherMixin, ExponentialBackoffMixin, SerializableMixin

if TYPE_CHECKING:
    from griptape.artifacts.audio_artifact import AudioArtifact


@define
class BaseTextToSpeechDriver(SerializableMixin, ExponentialBackoffMixin, EventPublisherMixin, ABC):
    model: str = field(kw_only=True, metadata={"serializable": True})

    def before_run(self, prompts: list[str]) -> None:
        self.publish_event(StartTextToSpeechEvent(prompts=prompts))

    def after_run(self) -> None:
        self.publish_event(FinishTextToSpeechEvent())

    def run_text_to_audio(self, prompts: list[str]) -> AudioArtifact:
        for attempt in self.retrying():
            with attempt:
                self.before_run(prompts)
                result = self.try_text_to_audio(prompts)
                self.after_run()

                return result

        else:
            raise Exception("Failed to run text to audio generation")

    @abstractmethod
    def try_text_to_audio(self, prompts: list[str]) -> AudioArtifact: ...
