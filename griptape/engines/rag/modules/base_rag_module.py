from abc import ABC
from concurrent import futures
from typing import Callable
from attrs import define, field, Factory
from griptape.utils import PromptStack


@define(kw_only=True)
class BaseRagModule(ABC):
    name: str = field(default=Factory(lambda self: self.class_name, takes_self=True), kw_only=True)
    futures_executor_fn: Callable[[], futures.Executor] = field(
        default=Factory(lambda: lambda: futures.ThreadPoolExecutor())
    )

    def generate_query_prompt_stack(self, system_prompt: str, query: str) -> PromptStack:
        return PromptStack(
            inputs=[
                PromptStack.Input(system_prompt, role=PromptStack.SYSTEM_ROLE),
                PromptStack.Input(query, role=PromptStack.USER_ROLE),
            ]
        )
