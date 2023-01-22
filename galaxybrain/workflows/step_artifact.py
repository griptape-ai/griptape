from abc import ABC
from typing import Optional

from attrs import define


@define
class StepArtifact(ABC):
    value: Optional[any]
