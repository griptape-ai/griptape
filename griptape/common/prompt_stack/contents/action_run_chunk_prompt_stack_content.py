from attrs import define, field

from griptape.common import BaseChunkPromptStackContent


@define
class ActionRunChunkPromptStackContent(BaseChunkPromptStackContent):
    content: str = field(kw_only=True)
    id: str = field(kw_only=True)
    name: str = field(kw_only=True)
    input: dict = field(kw_only=True)
