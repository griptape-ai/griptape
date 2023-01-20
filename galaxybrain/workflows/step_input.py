from attrs import define
from galaxybrain.workflows import StepArtifact


@define(frozen=True)
class StepInput(StepArtifact):
    pass
