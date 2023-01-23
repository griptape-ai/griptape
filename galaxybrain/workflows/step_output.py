from typing import Optional
from attrs import define, field
from galaxybrain.workflows.step_artifact import StepArtifact


@define(frozen=True)
class StepOutput(StepArtifact):
    meta: Optional[any] = field(default=None)
