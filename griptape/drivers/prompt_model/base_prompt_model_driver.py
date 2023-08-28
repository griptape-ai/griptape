from abc import ABC, abstractmethod
from typing import Union
from attr import define, field
from griptape.artifacts import TextArtifact
from griptape.utils import PromptStack
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import BaseTokenizer


@define
class BasePromptModelDriver(ABC):
    prompt_driver: BasePromptDriver = field(kw_only=True)
    tokenizer: BaseTokenizer = field(kw_only=True)

    @abstractmethod
    def prompt_stack_to_model_input(self, prompt_stack: PromptStack) -> Union[str, list]:
        ...

    @abstractmethod
    def prompt_stack_to_model_params(self, prompt_stack: PromptStack) -> dict:
        ...

    @abstractmethod
    def process_output(self, output: list[dict]) -> TextArtifact:
        ...
