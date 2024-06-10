from attrs import define, field

from typing import Optional
from griptape.common import BasePromptStackContent


@define
class BaseDeltaPromptStackContent(BasePromptStackContent):
    index: int = field(kw_only=True, metadata={"serializable": True})
    role: Optional[str] = field(kw_only=True, default=None, metadata={"serializable": True})
