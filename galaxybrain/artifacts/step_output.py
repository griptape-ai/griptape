from typing import Optional
from attrs import define, field
from galaxybrain.artifacts import StepArtifact


@define(frozen=True)
class StepOutput(StepArtifact):
    meta: Optional[any] = field(default=None)
