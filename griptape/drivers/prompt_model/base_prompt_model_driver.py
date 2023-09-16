from abc import ABC, abstractmethod
from typing import Union, Optional
from attr import define, field
from griptape.artifacts import TextArtifact
from griptape.utils import PromptStack
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import BaseTokenizer


@define
class BasePromptModelDriver(ABC):
    max_tokens: int = field(default=600, kw_only=True)
    prompt_driver: Optional[BasePromptDriver] = field(default=None, kw_only=True)
    tokenizer: BaseTokenizer

    @abstractmethod
    def prompt_stack_to_model_input(self, prompt_stack: PromptStack) -> Union[str, list]:
        ...

    @abstractmethod
    def prompt_stack_to_model_params(self, prompt_stack: PromptStack) -> dict:
        ...

    @abstractmethod
    def process_output(self, output: list[dict]) -> TextArtifact:
        ...
