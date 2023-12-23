import json
from abc import ABC, abstractmethod
from attr import define


@define
class BaseMetaEntry(ABC):
    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @abstractmethod
    def to_dict(self) -> dict:
        ...
