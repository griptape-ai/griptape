from typing import Callable, Dict, List, Any
from .base_processors import BasePromptStackProcessor
from griptape.artifacts import TextArtifact
from griptape.utils import PromptStack
import attr


@attr.s
class PromptDriverPiiProcessor(BasePromptStackProcessor):
    prompt_driver = attr.ib()
    mask_pii_func = attr.ib()
    unmask_pii_func = attr.ib()
    pii_replacements: Dict[str, str] = attr.ib(factory=dict)

    def before_run(self, prompt_stack: PromptStack) -> PromptStack:
        for input_item in prompt_stack.inputs:
            masked_text, replacements = self.mask_pii_func(input_item.content)
            input_item.content = masked_text
            self.pii_replacements.update(replacements)
        return prompt_stack

    def after_run(self, result: TextArtifact) -> TextArtifact:
        result.value = self.unmask_pii_func(result.value, self.pii_replacements)
        return result

    def mask_pii(self, text: str) -> str:
        original_text = text
        text = self.mask_pii_func(text)

        self.pii_replacements[original_text] = text

        return text

    def unmask_pii(self, text: str) -> str:
        return self.unmask_pii_func(text)
