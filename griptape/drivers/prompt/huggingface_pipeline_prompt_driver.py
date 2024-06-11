from __future__ import annotations
from collections.abc import Iterator

from typing import TYPE_CHECKING
from attrs import Factory, define, field

from griptape.artifacts import TextArtifact
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import HuggingFaceTokenizer
from griptape.utils import PromptStack, import_optional_dependency

if TYPE_CHECKING:
    from transformers import TextGenerationPipeline


@define
class HuggingFacePipelinePromptDriver(BasePromptDriver):
    """
    Attributes:
        params: Custom model run parameters.
        model: Hugging Face Hub model name.

    """

    max_tokens: int = field(default=250, kw_only=True, metadata={"serializable": True})
    model: str = field(kw_only=True, metadata={"serializable": True})
    params: dict = field(factory=dict, kw_only=True, metadata={"serializable": True})
    tokenizer: HuggingFaceTokenizer = field(
        default=Factory(
            lambda self: HuggingFaceTokenizer(model=self.model, max_output_tokens=self.max_tokens), takes_self=True
        ),
        kw_only=True,
    )
    pipe: TextGenerationPipeline = field(
        default=Factory(
            lambda self: import_optional_dependency("transformers").pipeline(
                "text-generation", model=self.model, max_new_tokens=self.max_tokens, tokenizer=self.tokenizer.tokenizer
            ),
            takes_self=True,
        )
    )

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        messages = [self._prompt_stack_input_to_message(input) for input in prompt_stack.inputs]

        result = self.pipe(
            messages,
            max_new_tokens=self.max_tokens,
            tokenizer=self.tokenizer.tokenizer,
            stop_strings=self.tokenizer.stop_sequences,
            temperature=self.temperature,
            do_sample=True,
        )

        if isinstance(result, list):
            if len(result) == 1:
                generated_text = result[0]["generated_text"][-1]["content"]

                return TextArtifact(value=generated_text)
            else:
                raise Exception("completion with more than one choice is not supported yet")
        else:
            raise Exception("invalid output format")

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextArtifact]:
        raise NotImplementedError("streaming is not supported")

    def prompt_stack_to_string(self, prompt_stack: PromptStack) -> str:
        return self.tokenizer.tokenizer.decode(self.__prompt_stack_to_tokens(prompt_stack))

    def _prompt_stack_input_to_message(self, prompt_input: PromptStack.Input) -> dict:
        return {"role": prompt_input.role, "content": prompt_input.content}

    def __prompt_stack_to_tokens(self, prompt_stack: PromptStack) -> list[int]:
        tokens = self.tokenizer.tokenizer.apply_chat_template(
            [self._prompt_stack_input_to_message(i) for i in prompt_stack.inputs],
            add_generation_prompt=True,
            tokenize=True,
        )

        if isinstance(tokens, list):
            return tokens
        else:
            raise ValueError("Invalid output type.")
