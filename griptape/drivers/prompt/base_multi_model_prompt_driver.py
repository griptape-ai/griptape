from __future__ import annotations
from attrs import define, field
from abc import ABC
from .base_prompt_driver import BasePromptDriver
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from griptape.tokenizers import BaseTokenizer
    from griptape.drivers import BasePromptModelDriver


@define
class BaseMultiModelPromptDriver(BasePromptDriver, ABC):
    """Prompt Driver for platforms like Amazon SageMaker, and Amazon Bedrock that host many LLM models.

    Instances of this Prompt Driver require a Prompt Model Driver which is used to convert the prompt stack
    into a model input and parameters, and to process the model output.

    Attributes:
        model: Name of the model to use.
        tokenizer: Tokenizer to use. Defaults to the Tokenizer of the Prompt Model Driver.
        prompt_model_driver: Prompt Model Driver to use.
    """

    tokenizer: BaseTokenizer | None = field(default=None, kw_only=True)
    prompt_model_driver: BasePromptModelDriver = field(kw_only=True)
    stream: bool = field(default=False, kw_only=True)

    @stream.validator
    def validate_stream(self, _, stream):
        if stream and not self.prompt_model_driver.supports_streaming:
            raise ValueError(f"{self.prompt_model_driver.__class__.__name__} does not support streaming")

    def __attrs_post_init__(self) -> None:
        self.prompt_model_driver.prompt_driver = self

        if not self.tokenizer:
            self.tokenizer = self.prompt_model_driver.tokenizer
