from __future__ import annotations

from typing import Any

from attrs import define, field

from griptape.common import BasePromptStackContent

from .base_prompt_stack_element import BasePromptStackElement


@define
class PromptStackElement(BasePromptStackElement):
    content: BasePromptStackContent | list[BasePromptStackContent] = field(
        kw_only=True, metadata={"serializable": True}
    )

    @property
    def value(self) -> Any:
        if isinstance(self.content, list):
            return [content.artifact for content in self.content]
        else:
            return self.content.artifact.value

    def to_text(self) -> str:
        return self.value.to_text()
