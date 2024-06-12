from __future__ import annotations
from typing import Optional, Any

from attrs import define, field

from griptape.common.prompt_stack.contents.delta_text_prompt_stack_content import DeltaTextPromptStackContent


from .base_prompt_stack_element import BasePromptStackElement


@define
class DeltaPromptStackElement(BasePromptStackElement):
    @define
    class DeltaUsage:
        input_tokens: Optional[float] = field(kw_only=True, default=None, metadata={"serializable": True})
        output_tokens: Optional[float] = field(kw_only=True, default=None, metadata={"serializable": True})

        @property
        def total_tokens(self) -> float:
            return (self.input_tokens or 0) + (self.output_tokens or 0)

        def __add__(self, other: DeltaPromptStackElement.DeltaUsage) -> DeltaPromptStackElement.DeltaUsage:
            return DeltaPromptStackElement.DeltaUsage(
                input_tokens=(self.input_tokens or 0) + (other.input_tokens or 0),
                output_tokens=(self.output_tokens or 0) + (other.output_tokens or 0),
            )

    role: Optional[str] = field(kw_only=True, default=None, metadata={"serializable": True})
    delta_content: Optional[DeltaTextPromptStackContent] = field(
        kw_only=True, default=None, metadata={"serializable": True}
    )
    delta_usage: DeltaUsage = field(kw_only=True, default=DeltaUsage(), metadata={"serializable": True})

    @property
    def value(self) -> Any:
        if self.delta_content is not None:
            return self.delta_content.text

    def to_text(self) -> str:
        return self.value.to_text()
