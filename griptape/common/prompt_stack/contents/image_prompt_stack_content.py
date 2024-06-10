from attrs import define, field

from griptape.common import BasePromptStackContent
from griptape.artifacts import ImageArtifact


@define
class ImagePromptStackContent(BasePromptStackContent):
    artifact: ImageArtifact = field(metadata={"serializable": True})
