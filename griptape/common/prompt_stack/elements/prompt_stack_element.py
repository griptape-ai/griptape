from __future__ import annotations
from attrs import define, field
from typing import Any

from griptape.common import BasePromptStackContent

from .base_prompt_stack_element import BasePromptStackElement


@define
class PromptStackElement(BasePromptStackElement):
    content: BasePromptStackContent | list[BasePromptStackContent] = field(metadata={"serializable": True})

    @property
    def value(self) -> Any:
        if isinstance(self.content, list):
            return [content.value for content in self.content]
        else:
            return self.content.value

    def to_text(self) -> str:
        return self.value.to_text()
