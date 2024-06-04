from attrs import define, field

from griptape.common import BasePromptStackContent
from griptape.artifacts import TextArtifact


@define
class TextPromptStackContent(BasePromptStackContent):
    value: TextArtifact = field(metadata={"serializable": True})
