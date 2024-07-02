from abc import ABC
from concurrent import futures
from typing import Callable

from attrs import define, field, Factory

from griptape.common import PromptStack, Message


@define(kw_only=True)
class BaseRagModule(ABC):
    futures_executor_fn: Callable[[], futures.Executor] = field(
        default=Factory(lambda: lambda: futures.ThreadPoolExecutor())
    )

    def generate_query_prompt_stack(self, system_prompt: str, query: str) -> PromptStack:
        return PromptStack(
            messages=[Message(system_prompt, role=Message.SYSTEM_ROLE), Message(query, role=Message.USER_ROLE)]
        )
