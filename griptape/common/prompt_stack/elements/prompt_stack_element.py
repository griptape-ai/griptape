from attrs import define, field

from griptape.common import BasePromptStackContent

from .base_prompt_stack_element import BasePromptStackElement


@define
class PromptStackElement(BasePromptStackElement):
    content: BasePromptStackContent = field(metadata={"serializable": True})
