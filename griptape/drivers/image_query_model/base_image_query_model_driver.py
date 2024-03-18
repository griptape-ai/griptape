from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from attr import define
from griptape.artifacts import TextArtifact
from griptape.mixins import SerializableMixin

@define
class BaseImageQueryModelDriver(SerializableMixin, ABC):
    @abstractmethod
    def query_image_request_parameters(self) -> dict:
        ...

    @abstractmethod
    def process_output(self, output: Any) -> TextArtifact:
        ...