from attrs import define, field

from griptape.common import BasePromptStackContent
from griptape.artifacts import TextArtifact


@define
class TextPromptStackContent(BasePromptStackContent):
    content: TextArtifact = field(metadata={"serializable": True})
