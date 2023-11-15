from typing import Callable, Dict, List, Any
from .base_processors import BasePromptStackProcessor
import attr


@attr.s
class PromptDriverPiiProcessor(BasePromptStackProcessor):
    prompt_driver = attr.ib()
    mask_pii_func = attr.ib()
    unmask_pii_func = attr.ib()

    def before_run(self, prompt_stack: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        for input_item in prompt_stack["inputs"]:
            input_item["content"] = self.mask_pii_func(input_item["content"])
        return prompt_stack

    def after_run(self, prompt_stack: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        for input_item in prompt_stack["inputs"]:
            input_item["content"] = self.unmask_pii_func(input_item["content"])
        return prompt_stack

    def mask_pii(self, text: str) -> str:
        return self.mask_pii_func(text)

    def unmask_pii(self, text: str) -> str:
        return self.unmask_pii_func(text)
