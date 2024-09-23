from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from attrs import define

from griptape.events import EventBus, FinishVideoGenerationEvent, StartVideoGenerationEvent
from griptape.mixins.exponential_backoff_mixin import ExponentialBackoffMixin
from griptape.mixins.serializable_mixin import SerializableMixin

if TYPE_CHECKING:
    from griptape.artifacts import VideoArtifact


@define
class BaseVideoGenerationDriver(SerializableMixin, ExponentialBackoffMixin, ABC):
    def before_run(self, prompt: str) -> None:
        EventBus.publish_event(StartVideoGenerationEvent(prompt=prompt))

    def after_run(self) -> None:
        EventBus.publish_event(FinishVideoGenerationEvent())

    def run_text_to_video(self, prompt: str) -> VideoArtifact:
        for attempt in self.retrying():
            with attempt:
                self.before_run(prompt)
                result = self.try_text_to_video(prompt)
                self.after_run()

                return result
        else:
            raise Exception("Failed to run text to video generation")

    @abstractmethod
    def try_text_to_video(self, prompt: str) -> VideoArtifact: ...
