from abc import ABC
from typing import Optional
from attr import define, field


@define
class BaseArtifact(ABC):
    value: Optional[any] = field()
