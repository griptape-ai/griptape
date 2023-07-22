import ai21
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.drivers import BasePromptDriver
from griptape.tokenizers.ai21_tokenizer import Ai21Tokenizer
from griptape.utils import PromptStack


@define
class Ai21PromptDriver(BasePromptDriver):
    api_key: str = field(kw_only=True)
    model: str = field(default=Ai21Tokenizer.DEFAULT_MODEL, kw_only=True)
    tokenizer: Ai21Tokenizer = field(
        default=Factory(
            lambda self: Ai21Tokenizer(model=self.model, api_key=self.api_key),
            takes_self=True,
        ),
        kw_only=True,
    )

    def default_prompt_stack_to_string_converter(
        self, prompt_stack: PromptStack
    ) -> str:
        prompt_lines = []

        for i in prompt_stack.inputs:
            if i.is_user():
                prompt_lines.append(f"User: {i.content}")
            elif i.is_assistant():
                prompt_lines.append(f"Assistant: {i.content}")
            elif i.is_system():
                prompt_lines.append(f"System: {i.content}")

        return "\n\n".join(prompt_lines)

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        result = ai21.Completion.execute(
            model=self.model,
            prompt=self.prompt_stack_to_string(prompt_stack),
            numResults=1,
            maxTokens=self.tokenizer.tokens_left(
                self.prompt_stack_to_string(prompt_stack)
            ),
            temperature=self.temperature,
            stopSequences=self.tokenizer.stop_sequences,
        )

        generation = result.completions[0].data.text

        return TextArtifact(generation)
