from __future__ import annotations
from attrs import define, field

from griptape.common import BaseDeltaPromptStackContent


@define
class TextDeltaPromptStackContent(BaseDeltaPromptStackContent):
    text: str = field(metadata={"serializable": True})
