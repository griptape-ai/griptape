from .base_processors import BasePromptStackProcessor


class PromptDriverPiiProcessor(BasePromptStackProcessor):
    def __init__(self, prompt_driver, mask_pii_func, unmask_pii_func):
        self.prompt_driver = prompt_driver
        self.mask_pii_func = mask_pii_func
        self.unmask_pii_func = unmask_pii_func

    def before_run(self, prompt_stack):
        for input_item in prompt_stack["inputs"]:
            input_item["content"] = self.mask_pii_func(input_item["content"])
        return prompt_stack

    def after_run(self, prompt_stack):
        for input_item in prompt_stack["inputs"]:
            input_item["content"] = self.unmask_pii_func(input_item["content"])
        return prompt_stack

    def mask_pii(self, text):
        return self.mask_pii_func(text)

    def unmask_pii(self, text):
        return self.unmask_pii_func(text)
