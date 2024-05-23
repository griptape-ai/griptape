from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from attrs import define, field
from griptape.artifacts import TextArtifact
from griptape.common import PromptStack
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import BaseTokenizer
from griptape.mixins import SerializableMixin


@define
class BasePromptModelDriver(SerializableMixin, ABC):
    max_tokens: Optional[int] = field(default=None, kw_only=True)
    prompt_driver: Optional[BasePromptDriver] = field(default=None, kw_only=True)
    supports_streaming: bool = field(default=True, kw_only=True)

    @property
    @abstractmethod
    def tokenizer(self) -> BaseTokenizer: ...

    @abstractmethod
    def prompt_stack_to_model_input(self, prompt_stack: PromptStack) -> str | list | dict: ...

    @abstractmethod
    def prompt_stack_to_model_params(self, prompt_stack: PromptStack) -> dict: ...

    @abstractmethod
    def process_output(self, output: list[dict] | str | bytes) -> TextArtifact: ...
