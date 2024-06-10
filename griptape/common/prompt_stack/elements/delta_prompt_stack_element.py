from typing import Optional, Any

from attrs import define, field

from griptape.common.prompt_stack.contents.delta_text_prompt_stack_content import DeltaTextPromptStackContent


from .base_prompt_stack_element import BasePromptStackElement


@define
class DeltaPromptStackElement(BasePromptStackElement):
    role: Optional[str] = field(kw_only=True, default=None, metadata={"serializable": True})
    delta_content: Optional[DeltaTextPromptStackContent] = field(
        kw_only=True, default=None, metadata={"serializable": True}
    )

    @property
    def value(self) -> Any:
        if self.delta_content is not None:
            return self.delta_content.artifact.value

    def to_text(self) -> str:
        return self.value.to_text()
