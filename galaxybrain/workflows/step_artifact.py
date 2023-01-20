from abc import ABC
from attrs import define


@define
class StepArtifact(ABC):
    value: any
