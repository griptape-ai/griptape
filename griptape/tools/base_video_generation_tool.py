from attrs import define

from griptape.mixins.artifact_file_output_mixin import ArtifactFileOutputMixin
from griptape.tools import BaseTool


@define
class BaseVideoGenerationTool(ArtifactFileOutputMixin, BaseTool):
    """A base class for tools that generate videos from text prompts."""

    PROMPT_DESCRIPTION = "Features and qualities to include in the generated video, descriptive and succinct."
