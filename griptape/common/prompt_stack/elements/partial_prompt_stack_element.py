from typing import Optional, Any

from attrs import define, field

from griptape.common.prompt_stack.contents.text_delta_prompt_stack_content import TextDeltaPromptStackContent


from .base_prompt_stack_element import BasePromptStackElement


@define
class PartialPromptStackElement(BasePromptStackElement):
    index: int = field(kw_only=True, metadata={"serializable": True})
    role: Optional[str] = field(kw_only=True, default=None, metadata={"serializable": True})
    content_delta: Optional[TextDeltaPromptStackContent] = field(
        kw_only=True, default=None, metadata={"serializable": True}
    )

    @property
    def value(self) -> Any:
        if self.content_delta is not None:
            return self.content_delta.value

    def to_text(self) -> str:
        return self.value.to_text()
