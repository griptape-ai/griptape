from __future__ import annotations

from typing import Any

from attrs import define, field, Factory

from griptape.common import BasePromptStackContent

from .base_prompt_stack_element import BasePromptStackElement


@define
class PromptStackElement(BasePromptStackElement):
    @define
    class Usage:
        input_tokens: int = field(kw_only=True, default=0, metadata={"serializable": True})
        output_tokens: int = field(kw_only=True, default=0, metadata={"serializable": True})

        @property
        def total_tokens(self) -> int:
            return self.input_tokens + self.output_tokens

    content: list[BasePromptStackContent] = field(kw_only=True, metadata={"serializable": True})
    usage: Usage = field(
        kw_only=True, default=Factory(lambda: PromptStackElement.Usage()), metadata={"serializable": True}
    )

    @property
    def value(self) -> Any:
        if isinstance(self.content, list):
            return [content.artifact for content in self.content]
        else:
            return self.content.artifact.value

    def to_text(self) -> str:
        return self.value.to_text()
