from attrs import define, field

from griptape.artifacts import TextArtifact
from griptape.common import BaseDeltaPromptStackContent


@define
class DeltaTextPromptStackContent(BaseDeltaPromptStackContent):
    artifact: TextArtifact = field(metadata={"serializable": True})
