import json
from abc import ABC, abstractmethod
from attr import define

from griptape.mixins import SerializableMixin


@define
class BaseMetaEntry(SerializableMixin, ABC):
    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @abstractmethod
    def to_dict(self) -> dict:
        ...
