from attrs import define, field

from griptape.common import BasePromptStackContent


@define
class ActionRunPromptStackContent(BasePromptStackContent):
    id: str = field(kw_only=True)
    name: str = field(kw_only=True)
    input: dict = field(kw_only=True)
