from attrs import define, field

from griptape.common import BasePromptStackContent
from griptape.artifacts import ImageArtifact


@define
class ImagePromptStackContent(BasePromptStackContent):
    content: ImageArtifact = field(metadata={"serializable": True})
