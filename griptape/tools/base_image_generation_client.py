from attrs import define

from griptape.mixins import BlobArtifactFileOutputMixin
from griptape.tools import BaseTool


@define
class BaseImageGenerationClient(BlobArtifactFileOutputMixin, BaseTool):
    """A base class for tools that generate images from text prompts."""

    PROMPT_DESCRIPTION = "Features and qualities to include in the generated image, descriptive and succinct."
    NEGATIVE_PROMPT_DESCRIPTION = (
        "Features and qualities to avoid in the generated image. Affirmatively describe "
        "what to avoid, for example: to avoid the color red, include 'red' "
        "rather than 'no red'."
    )
