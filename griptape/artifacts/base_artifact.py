import json
from abc import ABC, abstractmethod
from typing import Optional
from attr import define, field, Factory


@define
class BaseArtifact(ABC):
    value: Optional[any] = field()
    type: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)

    @abstractmethod
    def __str__(self):
        ...
