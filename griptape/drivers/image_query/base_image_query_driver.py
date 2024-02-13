from __future__ import annotations

from abc import abstractmethod, ABC
from typing import Optional, TYPE_CHECKING

from attr import define, field

from griptape.artifacts import TextArtifact, ImageArtifact
from griptape.events import StartImageQueryEvent, FinishImageQueryEvent
from griptape.mixins import ExponentialBackoffMixin, SerializableMixin

if TYPE_CHECKING:
    from griptape.structures import Structure


@define
class BaseImageQueryDriver(SerializableMixin, ExponentialBackoffMixin, ABC):
    structure: Optional[Structure] = field(default=None, kw_only=True)

    def before_run(self, query: str, images: list[ImageArtifact]) -> None:
        if self.structure:
            self.structure.publish_event(
                StartImageQueryEvent(query=query, images_info=[image.to_text() for image in images])
            )

    def after_run(self, result: str) -> None:
        if self.structure:
            self.structure.publish_event(FinishImageQueryEvent(result=result))

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
    def try_query(self, query: str, images: list[ImageArtifact]) -> TextArtifact:
        ...
