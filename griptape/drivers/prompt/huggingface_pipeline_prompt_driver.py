from __future__ import annotations
from collections.abc import Iterator

from typing import TYPE_CHECKING
from attrs import Factory, define, field

from griptape.artifacts import TextArtifact
from griptape.common import PromptStack
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import HuggingFaceTokenizer
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from transformers import TextGenerationPipeline

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
        messages = [{"role": input.role, "content": input.content} for input in prompt_stack.inputs]

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
