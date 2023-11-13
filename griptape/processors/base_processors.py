class BasePromptStackProcessor:
    def before_run(self, prompt):
        # Process the prompt before it is run
        pass

    def after_run(self, result):
        # Process the result after the prompt is run
        pass


class BasePromptDriver:
    def __init__(self):
        self.prompt_stack_processors = []

    def before_run(self, prompt):
        for processor in self.prompt_stack_processors:
            prompt = processor.before_run(prompt)
        return prompt

    def after_run(self, result):
        for processor in self.prompt_stack_processors:
            result = processor.after_run(result)
        return result
