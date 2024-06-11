from __future__ import annotations

from typing import Any, Optional

from attrs import define, field, Factory

from griptape.common import BasePromptStackContent

from .base_prompt_stack_element import BasePromptStackElement


@define
class PromptStackElement(BasePromptStackElement):
    @define
    class Usage:
        input_tokens: Optional[float] = field(kw_only=True, default=None, metadata={"serializable": True})
        output_tokens: Optional[float] = field(kw_only=True, default=None, metadata={"serializable": True})

        @property
        def total_tokens(self) -> float:
            return (self.input_tokens or 0) + (self.output_tokens or 0)

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
