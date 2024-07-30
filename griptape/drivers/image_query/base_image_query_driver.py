from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from attrs import define, field

from griptape.events import FinishImageQueryEvent, StartImageQueryEvent
from griptape.mixins import EventPublisherMixin, ExponentialBackoffMixin, SerializableMixin

if TYPE_CHECKING:
    from griptape.artifacts import ImageArtifact, TextArtifact


@define
class BaseImageQueryDriver(EventPublisherMixin, SerializableMixin, ExponentialBackoffMixin, ABC):
    max_tokens: int = field(default=256, kw_only=True, metadata={"serializable": True})

    def before_run(self, query: str, images: list[ImageArtifact]) -> None:
        self.publish_event(
            StartImageQueryEvent(query=query, images_info=[image.to_text() for image in images]),
        )

    def after_run(self, result: str) -> None:
        self.publish_event(FinishImageQueryEvent(result=result))

    def query(self, query: str, images: list[ImageArtifact]) -> TextArtifact:
        for attempt in self.retrying():
            with attempt:
                self.before_run(query, images)

                result = self.try_query(query, images)

                self.after_run(result.value)

                return result
        else:
            raise Exception("image query driver failed after all retry attempts")

    @abstractmethod
    def try_query(self, query: str, images: list[ImageArtifact]) -> TextArtifact: ...
