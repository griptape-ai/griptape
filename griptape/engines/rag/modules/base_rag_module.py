from abc import ABC
from concurrent import futures
from typing import Callable, Any, Optional
from attrs import define, field, Factory
from griptape.engines.rag import RagContext
from griptape.common import PromptStack, Message


@define(kw_only=True)
class BaseRagModule(ABC):
    name: str = field(default=Factory(lambda self: self.__class__.__name__, takes_self=True), kw_only=True)
    futures_executor_fn: Callable[[], futures.Executor] = field(
        default=Factory(lambda: lambda: futures.ThreadPoolExecutor())
    )

    def generate_query_prompt_stack(self, system_prompt: str, query: str) -> PromptStack:
        return PromptStack(
            messages=[Message(system_prompt, role=Message.SYSTEM_ROLE), Message(query, role=Message.USER_ROLE)]
        )

    def get_context_param(self, context: RagContext, key: str) -> Optional[Any]:
        return context.module_configs.get(self.name, {}).get(key)

    def set_context_param(self, context: RagContext, key: str, value: Any) -> None:
        if not isinstance(context.module_configs.get(self.name), dict):
            context.module_configs[self.name] = {}

        context.module_configs[self.name][key] = value
