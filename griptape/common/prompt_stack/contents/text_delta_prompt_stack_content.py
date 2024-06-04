from attrs import define, field

from griptape.common import BaseChunkPromptStackContent


@define
class TextDeltaPromptStackContent(BaseChunkPromptStackContent):
    value: str = field(metadata={"serializable": True})
