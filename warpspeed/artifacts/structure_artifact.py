from abc import ABC
from typing import Optional
from attrs import define, field


@define
class StructureArtifact(ABC):
    value: Optional[any] = field()
