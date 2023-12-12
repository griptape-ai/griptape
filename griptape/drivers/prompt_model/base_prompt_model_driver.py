from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from attr import define, field
from griptape.artifacts import TextArtifact
from griptape.utils import PromptStack
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import BaseTokenizer


@define
class BasePromptModelDriver(ABC):
    max_tokens: int = field(default=600, kw_only=True)
    prompt_driver: BasePromptDriver | None = field(default=None, kw_only=True)
    supports_streaming: bool = field(default=True, kw_only=True)

    @property
    @abstractmethod
    def tokenizer(self) -> BaseTokenizer:
        ...

    @abstractmethod
    def prompt_stack_to_model_input(self, prompt_stack: PromptStack) -> str | list | dict:
        ...

    @abstractmethod
    def prompt_stack_to_model_params(self, prompt_stack: PromptStack) -> dict:
        ...

    @abstractmethod
    def process_output(self, output: list[dict] | str | bytes) -> TextArtifact:
        ...
