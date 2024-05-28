from attrs import define, field

from griptape.artifacts import ListArtifact
from griptape.common import BasePromptStackContent


@define
class ActionResultPromptStackContent(BasePromptStackContent):
    content: ListArtifact = field(metadata={"serializable": True})
    action_id: str = field(kw_only=True)
