from attrs import define, field
from abc import ABC, abstractmethod
from typing import Optional
from galaxybrain.prompts.prompt import Prompt
from galaxybrain.completions.completion_result import CompletionResult
from galaxybrain.memory import Memory


@define
class Completion(ABC):
    memory: Optional[Memory] = field(default=None, kw_only=True)

    def __call__(self, prompt: any, memory: Optional[Memory] = None) -> CompletionResult:
        if isinstance(prompt, Prompt):
            return self.complete(prompt, memory)
        elif isinstance(prompt, str):
            return self.complete(Prompt(prompt, memory))
        else:
            raise Exception("Unknown prompt type")

    @abstractmethod
    def complete(self, prompt: Prompt, memory: Optional[Memory] = None) -> CompletionResult:
        pass

    