from __future__ import annotations
from abc import ABC, abstractmethod
from attrs import define
from griptape.mixins import SerializableMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from griptape.artifacts import TextArtifact, ImageArtifact


@define
class BaseImageQueryModelDriver(SerializableMixin, ABC):
    @abstractmethod
    def image_query_request_parameters(self, query: str, images: list[ImageArtifact], max_tokens: int) -> dict: ...

    @abstractmethod
    def process_output(self, output: dict) -> TextArtifact: ...
